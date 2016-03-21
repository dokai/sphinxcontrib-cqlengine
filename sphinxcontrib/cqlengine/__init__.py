# -*- coding: utf-8 -*-
"""Sphinx directives for cqlengine."""

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import GroupedField
from sphinxcontrib.blockdiag import blockdiag_node
from string import Template
import importlib


BLOCKDIAG_TEMPLATE_UNCLUSTERED = Template(u"""
blockdiag table {

    default_group_color = "#ffffff";
    default_fontsize = 15;

    class rest [
        textcolor="#999",
        stacked
        ];

    class row [
        color="#ccc",
        orientation="portrait"
        ];

    partition [
        label="${partition_key}",
        description="Partition (row) key"
        ];

    columns [
        shape="note",
        label="${columns}",
        description="Non-clustering data columns",
        height=${columns_height},
        width=${columns_width}
        ];

    partition_rest [
        class="rest",
        label=".. rows .."
        ];

    group rows {
        label = "Partitions";
        class = row;
        partition -> partition_rest [style="dashed"];
    }

    partition -> columns;
}
""".lstrip())

BLOCKDIAG_TEMPLATE_CLUSTERED = Template(u"""
blockdiag table {

    default_group_color = "#ffffff";
    default_fontsize = 15;

    class rest [
        textcolor="#999",
        stacked
        ];

    class row [
        color="#ccc",
        orientation="portrait"
        ];

    partition [
        label="${partition_key}",
        description="Partition (row) key",
        height=${partition_height}
        ];

    cluster [
        shape="roundedbox",
        label="${clustering_key}",
        description="Clustering keys",
        height=${cluster_height}
        ];

    columns [
        shape="note",
        label="${columns}",
        description="Non-clustering data columns",
        height=${columns_height},
        width=${columns_width}
        ];

    partition_rest [
        class="rest",
        label=".. rows .."
        ];

    cluster_rest [
        class="rest",
        shape="roundedbox",
        label=".. clusters .."
        ];

    columns_rest [
        class="rest",
        shape="note",
        label=".. columns .."
        ];

    partition -> cluster;
    cluster -> cluster_rest [style="dashed"];

    group rows {
        label = "Cassandra rows";
        class = row;
        partition -> partition_rest [style="dashed"];
    }

    group {
        label = "Cassandra column clusters";
        group columns {
            orientation = portrait;
            color = "#eee";
            cluster -> columns;
        }

        group rest {
            orientation = portrait;
            cluster_rest -> columns_rest [style="dashed"];
        }
    }
}
""".lstrip())


class CassandraTable(ObjectDescription):
    """Sphinx directive to automatically document a Cassandra table modeled
    using cqlengine.

    This directive introspects the cqlengine model class to determine the CQL
    table name, the partition key, clustering keys and secondary indexes. In
    addition it uses `blockdiag <http://blockdiag.com/en/blockdiag/index.html>`_
    to generate a diagram of the table data model in Cassandra.

    Usage::

        .. cassandra:: module.path.to.SomeModel
    """

    doc_field_types = [
        GroupedField('partitionkey',
            label='Partition key', names=('partitionkey', 'pkey')),
        GroupedField('clusteringkey',
            label='Clustering key', names=('clusteringkey', 'ckey')),
        GroupedField('indexes',
            label='Secondary indexes', names=('index', 'secondaryindex')),
        GroupedField('datacolumns',
            label='Data columns', names=('datacolumn', 'column')),
    ]

    def model_metadata(self):
        modname, classname = self.arguments[0].rsplit(u'.', 1)
        module = importlib.import_module(modname)
        klass = getattr(module, classname)

        def metacol(name, column):
            return (
                name,
                u'{}.{}'.format(klass.__name__, name),
                u'{}.{}'.format(column.__class__.__module__, column.__class__.__name__),
                column.partition_key,
                u'ASC' if column.clustering_order is None else u'DESC')

        primary_keys = [
            metacol(name, col)
            for name, col
            in klass._primary_keys.items()]
        pk_set = {name for name, _, _, _, _ in primary_keys}
        indexes = []
        columns = []

        partition_keys = [primary_keys[0]]
        partition_keys.extend([k for k in primary_keys[1:] if k[3]])

        clustering_keys = [k for k in primary_keys if not k[3]]

        for name, col in klass._columns.items():
            metadata = metacol(name, col)
            if col.index:
                indexes.append(metadata)
            if name not in pk_set:
                columns.append(metadata)

        return {
            'classname': klass.__name__,
            'tablename': klass.column_family_name(False),
            'indexes': indexes,
            'columns': columns,
            'partitionkey': partition_keys,
            'clusteringkey': clustering_keys,
        }

        return klass.__name__, klass.column_family_name(False)

    def needs_arglist(self):
        return False

    def run(self):
        metadata = self.model_metadata()

        # Update the contents with autogenerated Cassandra table metadata.
        params = [u'']
        for short, long, classname, _, _ in metadata['partitionkey']:
            params.append(u':partitionkey {}: :class:`{}` (:class:`~{}`)'.format(short, long, classname))
        for short, long, classname, _, order in metadata['clusteringkey']:
            params.append(u':clusteringkey {} «{}»: :class:`{}` (:class:`~{}`)'.format(short, order, long, classname))
        for short, long, classname, _, _ in metadata['indexes']:
            params.append(u':index {}: :class:`{}` (:class:`~{}`)'.format(short, long, classname))
        for short, long, classname, _, _ in metadata['columns']:
            params.append(u':column {}: :class:`{}` (:class:`~{}`)'.format(short, long, classname))
        self.content.data.extend(params)

        # Render the parameter nodes using the super class.
        results = super(self.__class__, self).run()

        # Replace the signature with the Cassandra table name generated by
        # cqlengine.
        table = u'CQL TABLE: {}'.format(metadata['tablename'])
        results[1][0][0].replace_self(addnodes.desc_name(table, table))

        # Create the Blockdiag node to render the table diagram.
        def boxwidth(lines, charwidth=10, default=10):
            if len(lines) == 0:
                return default * charwidth
            return charwidth * max(default, max(len(l) for l in lines))

        def boxheight(num_lines, lineheight=20, default=2):
            return max(lineheight * default, lineheight * num_lines)

        def boxvalues(cols):
            if len(cols) == 0:
                return u'<<n/a>>'

            return u'\n'.join(c[0] for c in cols)

        diagram = blockdiag_node()
        if len(metadata['clusteringkey']) > 0:
            diagram['code'] = BLOCKDIAG_TEMPLATE_CLUSTERED.substitute(
                partition_key=boxvalues(metadata['partitionkey']),
                partition_height=boxheight(len(metadata['partitionkey'])),
                clustering_key=boxvalues(metadata['clusteringkey']),
                cluster_height=boxheight(len(metadata['clusteringkey'])),
                columns=boxvalues(metadata['columns']),
                columns_height=boxheight(len(metadata['columns'])),
                columns_width=boxwidth([(c[0]) for c in metadata['columns']]))
        else:
            diagram['code'] = BLOCKDIAG_TEMPLATE_UNCLUSTERED.substitute(
                partition_key=boxvalues(metadata['partitionkey']),
                partition_height=boxheight(len(metadata['partitionkey'])),
                columns=boxvalues(metadata['columns']),
                columns_height=boxheight(len(metadata['columns'])),
                columns_width=boxwidth([(c[0]) for c in metadata['columns']]))
        diagram['alt'] = self.arguments[0]
        diagram['caption'] = self.arguments[0]
        diagram['options'] = {}

        if 'maxwidth' in self.options:
            diagram['options']['maxwidth'] = self.options['maxwidth']
        if 'desctable' in self.options:
            diagram['options']['desctable'] = self.options['desctable']
        results.append(diagram)

        return results


def setup(app):
    """Registers the Sphinx extension."""
    app.add_directive('cassandra', CassandraTable)
