"""
Utility Functions
"""

# %% import libs

import xml.etree.ElementTree as ET

# %% pretty print an ElementTree
# ref: https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file
# NOTE: can be replaced by ET.indent(...) in python 3.9

def pretty_print(current, parent=None, index=-1, depth=0, indent=" "*2):
    for i, node in enumerate(current):
        pretty_print(node, current, i, depth + 1, indent)
    if parent is not None:
        if index == 0:
            parent.text = '\n' + (indent * depth)
        else:
            parent[index - 1].tail = '\n' + (indent * depth)
        if index == len(parent) - 1:
            current.tail = '\n' + (indent * (depth - 1))
        if current.text is not None: 
            if not current.text.strip(' '):
                current.text = '\n' + (indent * depth)
            elif current.text.strip():
                current.text = ' ' + current.text + ' '
            else:
                pass

# %% a decorator to update parent node and set it back

def update_parent(parent_name):
    def _update_parent(func):
        def _inner(self, *args, **kwargs):
            # backup self.parent
            parent = self.parent
            # update self.parent
            self.parent = ET.SubElement(self.parent, parent_name)
            # call func
            res = func(self, *args, **kwargs)
            # reset self.parent
            self.parent = parent
            return res
        return _inner
    return _update_parent
