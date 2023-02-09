"""
This file contains the data structures will be repeatedly used in this compiler project
"""

import collections

class Node:
    def __init__(self, node_type=None, node_value=None, parent=None, children=None):
        """
        :param node_type: Representing the type of node exists in the parse tree
        :param node_value: Representing the value of the node exists in the parse tree
        :param parent: Representing the parent of this node in the parse tree.
        :param children: Representing the children of this node in the parse tree.
        """
        self.node_type = node_type
        self.node_value = node_value
        self.parent = parent
        if children:
            self.children = list(children)
        else:
            self.children = []

        if self.parent:
            self.parent.add_children(self)

    # create in-class function for extend the children back to the the original list of children
    def add_children(self, *children):
        self.children.extend(children)
        for i in children:
            i.parent = self

    # compress the path of tree so that there is only one child in the hiearchy
    def tree_compression(self):
        parent = self.parent
        if not parent:
            return

        children = parent.children
        if len(children) != 1:
            return

        children_index = parent.parent.children.index(parent)
        self.parent = parent.parent
        self.parent.children[children_index] = self
        self.parent.tree_compression()

    def __repr__(self):
        return f'node: (title: {id(self)}, label: {self.node_value}, type: {self.node_type})'



