import numpy as np


class Node(object):
    """Node in a computation graph."""

    def __init__(self):
        """Constructor, new node is indirectly created by Op object __call__ method.

            Instance variables
            ------------------
            self.inputs: the list of input nodes.
            self.op: the associated op object,
                e.g. add_op object if this node is created by adding two other nodes.
            self.const_attr: the add or multiply constant,
                e.g. self.const_attr=5 if this node is created by x+5.
            self.name: node name for debugging purposes.
        """
        self.inputs = []
        self.op = None
        self.const_attr = None
        self.name = ""

    def __add__(self, other):
        """Adding two nodes return a new node."""
        if isinstance(other, Node):
            new_node = add_op(self, other)
        else:
            # Add by a constant stores the constant in the new node's const_attr field.
            # 'other' argument is a constant
            new_node = add_byconst_op(self, other)
        return new_node

    """mul_by_const (check)"""

    def __mul__(self, other):
        """TODO: Your code here"""
        # Multiply two node return a new node
        if isinstance(other, Node):
            new_node = mul_op(self, other)
        else:
            # Multiply by a constant stores the constant in the
            # new node's cons_attr field
            new_node = mul_byconst_op(self, other)
        return new_node

    def __truediv__(self, other):
        if isinstance(other, Node):
            new_node = div_op(self, other)
        else:
            new_node = div_byconst_op(self, other)
        return new_node

    def __rtruediv__(self, other):
        if isinstance(other, Node):
            new_node = div_op(self, other)
        else:
            new_node = rdiv_byconst_op(self, other)
        return new_node

    def __sub__(self, other):
        if isinstance(other, Node):
            new_node = sub_op(self, other)
        else:
            new_node = sub_byconst_op(self, other)
        return new_node

    def __rsub__(self, other):
        if isinstance(other, Node):
            new_node = sub_op(self, other)
        else:
            new_node = rsub_byconst_op(self, other)
        return new_node

    def __neg__(self):
        return neg_op(self)

    # Allow left-hand-side add and multiply.
    __radd__ = __add__
    __rmul__ = __mul__

    def __str__(self):
        """Allow print to display node name."""
        return self.name

    __repr__ = __str__


def Variable(name):
    """User defined variables in an expression.
        e.g. x = Variable(name = "x")
    """
    placeholder_node = placeholder_op()
    placeholder_node.name = name
    return placeholder_node


class Op(object):
    """Op represents operations performed on nodes."""

    def __call__(self):
        """Create a new node and associate the op object with the node.

        Returns
        -------
        The new node object.
        """
        """node here"""
        new_node = Node()
        new_node.op = self
        return new_node

    def compute(self, node, input_vals):
        """Given values of input nodes, compute the output value.

        Parameters
        ----------
        node: node that performs the compute.
        input_vals: values of input nodes.

        Returns
        -------
        An output value of the node.
        """
        raise NotImplementedError

    def gradient(self, node, output_grad):
        """Given value of output gradient, compute gradient contributions to each input node.

        Parameters
        ----------
        node: node that performs the gradient.
        output_grad: value of output gradient summed from children nodes' contributions

        Returns
        -------
        A list of gradient contributions to each input node respectively.
        """
        raise NotImplementedError


class AddOp(Op):
    """Op to element-wise add two nodes."""

    def __call__(self, node_A, node_B):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A, node_B]
        new_node.name = "(%s+%s)" % (node_A.name, node_B.name)
        return new_node

    def compute(self, node, input_vals):
        """Given values of two input nodes, return result of element-wise addition."""
        assert len(input_vals) == 2
        return input_vals[0] + input_vals[1]

    def gradient(self, node, output_grad):
        """Given gradient of add node, return gradient contributions to each input."""
        return [output_grad, output_grad]

class AddByConstOp(Op):
    """Op to element-wise add a nodes by a constant."""

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.const_attr = const_val
        new_node.inputs = [node_A]
        new_node.name = "(%s+%s)" % (node_A.name, str(const_val))
        return new_node

    def compute(self, node, input_vals):
        """Given values of input node, return result of element-wise addition."""
        assert len(input_vals) == 1
        return input_vals[0] + node.const_attr

    def gradient(self, node, output_grad):
        """Given gradient of add node, return gradient contribution to input."""
        return [output_grad]

class MulOp(Op):
    """Op to element-wise multiply two nodes."""

    def __call__(self, node_A, node_B):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A, node_B]
        new_node.name = "(%s*%s)" % (node_A.name, node_B.name)
        return new_node

    def compute(self, node, input_vals):
        """Given values of two input nodes, return result of element-wise multiplication."""
        """TODO: Your code here"""
        if not len(input_vals) == 2:
            raise AssertionError
        res = input_vals[0] * input_vals[1]
        return res

    def gradient(self, node, output_grad):
        """Given gradient of multiply node, return gradient contributions to each input."""
        """TODO: Your code here"""
        res = [node.inputs[1] * output_grad, output_grad * node.inputs[0]]
        return res

class MulByConstOp(Op):
    """Op to element-wise multiply a nodes by a constant."""

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.const_attr = const_val
        new_node.inputs = [node_A]
        new_node.name = "(%s*%s)" % (node_A.name, str(const_val))
        return new_node

    def compute(self, node, input_vals):
        """Given values of input node, return result of element-wise multiplication."""
        """TODO: Your code here"""
        if not len(input_vals) == 1:
            raise AssertionError
        res = input_vals[0] * node.const_attr
        return res

    def gradient(self, node, output_grad):
        """Given gradient of multiplication node, return gradient contribution to input."""
        """TODO: Your code here"""
        res = [output_grad * node.const_attr]
        return res

class MatMulOp(Op):
    """Op to matrix multiply two nodes."""

    def __call__(self, node_A, node_B, trans_A=False, trans_B=False):
        """Create a new node that is the result a matrix multiple of two input nodes.

        Parameters
        ----------
        node_A: lhs of matrix multiply
        node_B: rhs of matrix multiply
        trans_A: whether to transpose node_A
        trans_B: whether to transpose node_B

        Returns
        -------
        Returns a node that is the result a matrix multiple of two input nodes.
        """
        new_node = Op.__call__(self)
        new_node.matmul_attr_trans_A = trans_A
        new_node.matmul_attr_trans_B = trans_B
        new_node.inputs = [node_A, node_B]
        new_node.name = "MatMul(%s,%s,%s,%s)" % (node_A.name, node_B.name, str(trans_A), str(trans_B))
        return new_node

    def compute(self, node, input_vals):
        """Given values of input nodes, return result of matrix multiplication."""
        """TODO: Your code here"""
        if not len(input_vals) == 2:
            raise AssertionError
        if node.matmul_attr_trans_A and not node.matmul_attr_trans_B:
            res = np.matmul(np.transpose(input_vals[0]), input_vals[1])
            return res
        elif not node.matmul_attr_trans_A and node.matmul_attr_trans_B:
            res = np.matmul(input_vals[0], np.transpose(input_vals[1]))
            return res
        elif not node.matmul_attr_trans_A and not node.matmul_attr_trans_B:
            res = np.matmul(input_vals[0], input_vals[1])
            return res
        res = np.matmul(np.transpose(input_vals[0]), np.transpose(input_vals[1]))
        return res

    def gradient(self, node, output_grad):
        """Given gradient of multiply node, return gradient contributions to each input.

        Useful formula: if Y=AB, then dA=dY B^T, dB=A^T dY
        """
        """TODO: Your code here"""
        res = [matmul_op(output_grad, node.inputs[1], False, True), matmul_op(node.inputs[0], output_grad, True, False)]
        return res

# New
class DivOp(Op):

    def __call__(self, node_A, node_B):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A, node_B]
        new_node.name = "%s/%s" % (node_A.name, node_B.name)
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 2
        return input_vals[0] / input_vals[1]

    def gradient(self, node, output_grad):
        return [output_grad / node.inputs[1], -output_grad * node.inputs[0] / (node.inputs[1] * node.inputs[1])]

# New
class DivByConstOp(Op):

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A]
        new_node.const_attr = const_val
        new_node.name = "%s/%s" % (node_A.name, str(const_val))
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return input_vals[0] / node.const_attr

    def gradient(self, node, output_grad):
        return [output_grad / node.const_attr]

# New
class RDivByConstOp(Op):

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A]
        new_node.const_attr = const_val
        new_node.name = "%s/%s" % (str(const_val), node_A.name)
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return node.const_attr / input_vals[0]

    def gradient(self, node, output_grad):
        return [-output_grad * node.const_attr / (node.inputs[0] * node.inputs[0])]

# New
class NegOp(Op):

    def __call__(self, node):
        new_node = Op.__call__(self)
        new_node.inputs = [node]
        new_node.name = "-%s" % node.name
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return -input_vals[0]

    def gradient(self, node, output_grad):
        return [-output_grad]

# New
class SubOp(Op):

    def __call__(self, node_A, node_B):
        new_node = Op.__call__(self)
        new_node.inputs = [node_A, node_B]
        new_node.name = "%s-%s" % (node_A.name, node_B.name)
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 2
        return input_vals[0] - input_vals[1]

    def gradient(self, node, output_grad):
        return [output_grad, -output_grad]

# New
class SubByConstOp(Op):

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.const_attr = const_val
        new_node.inputs = [node_A]
        new_node.name = "(%s-%s)" % (node_A.name, str(const_val))
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return input_vals[0] - node.const_attr

    def gradient(self, node, output_grad):
        return [output_grad]

# New
class RSubByConstOp(Op):

    def __call__(self, node_A, const_val):
        new_node = Op.__call__(self)
        new_node.const_attr = const_val
        new_node.inputs = [node_A]
        new_node.name = "(%s-%s)" % (str(const_val), node_A.name)
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return node.const_attr - input_vals[0]

    def gradient(self, node, output_grad):
        return [-output_grad]

class PlaceholderOp(Op):
    """Op to feed value to a nodes."""

    def __call__(self):
        """Creates a variable node."""
        new_node = Op.__call__(self)
        return new_node

    def compute(self, node, input_vals):
        """No compute function since node value is fed directly in Executor."""
        assert False, "placeholder values provided by feed_dict"

    def gradient(self, node, output_grad):
        """No gradient function since node has no inputs."""
        return None

class ZerosLikeOp(Op):
    """Op that represents a constant np.zeros_like."""

    def __call__(self, node_A):
        """Creates a node that represents a np.zeros array of same shape as node_A."""
        new_node = Op.__call__(self)
        new_node.inputs = [node_A]
        new_node.name = "Zeroslike(%s)" % node_A.name
        return new_node

    def compute(self, node, input_vals):
        """Returns zeros_like of the same shape as input."""
        assert (isinstance(input_vals[0], np.ndarray))
        return np.zeros(input_vals[0].shape)

    def gradient(self, node, output_grad):
        return [zeroslike_op(node.inputs[0])]

class OnesLikeOp(Op):
    """Op that represents a constant np.ones_like."""

    def __call__(self, node_A):
        """Creates a node that represents a np.ones array of same shape as node_A."""
        new_node = Op.__call__(self)
        new_node.inputs = [node_A]
        new_node.name = "Oneslike(%s)" % node_A.name
        return new_node

    def compute(self, node, input_vals):
        """Returns ones_like of the same shape as input."""
        assert (isinstance(input_vals[0], np.ndarray))
        return np.ones(input_vals[0].shape)

    def gradient(self, node, output_grad):
        return [zeroslike_op(node.inputs[0])]

# New
class LogOp(Op):

    def __call__(self, node):
        new_node = Op.__call__(self)
        new_node.inputs = [node]
        new_node.name = "log(%s)" % node.name
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return np.log(input_vals[0])

    def gradient(self, node, output_grad):
        return [output_grad / node.inputs[0]]

# New
class ExpOp(Op):

    def __call__(self, node):
        new_node = Op.__call__(self)
        new_node.inputs = [node]
        new_node.name = "exp(%s)" % node.name
        return new_node

    def compute(self, node, input_vals):
        assert len(input_vals) == 1
        return np.exp(input_vals[0])

    def gradient(self, node, output_grad):
        return [output_grad * exp_op(node.inputs[0])]

# New
class ReduceSumOp(Op):

    def __call__(self, node):
        new_node = Op.__call__(self)
        new_node.inputs = [node]
        new_node.name = "reduce_sum(%s)" % node.name
        return new_node

    def compute(self, node, input_vals):
        assert isinstance(input_vals[0], np.ndarray)
        return np.sum(input_vals[0])

    def gradient(self, node, output_grad):
        return [output_grad * oneslike_op(node.inputs[0])]

# Create global singletons of operators.
add_op = AddOp()
mul_op = MulOp()
add_byconst_op = AddByConstOp()
mul_byconst_op = MulByConstOp()
matmul_op = MatMulOp()
placeholder_op = PlaceholderOp()
oneslike_op = OnesLikeOp()
zeroslike_op = ZerosLikeOp()

div_op = DivOp()
sub_op = SubOp()
neg_op = NegOp()
neg_op = NegOp()
add_byconst_op = AddByConstOp()
rsub_byconst_op = RSubByConstOp()
sub_byconst_op = SubByConstOp()
div_byconst_op = DivByConstOp()
rdiv_byconst_op = RDivByConstOp()
log_op = LogOp()
exp_op = ExpOp()
reduce_sum = ReduceSumOp()

def exp(val):
    if isinstance(val, Node):
        return exp_op(val)
    return np.exp(val)


def log(val):
    if isinstance(val, Node):
        return log_op(val)
    return np.log(val)


class Executor:
    """Executor computes values for a given subset of nodes in a computation graph."""

    def __init__(self, eval_node_list):
        """
        Parameters
        ----------
        eval_node_list: list of nodes whose values need to be computed.
        """
        self.eval_node_list = eval_node_list

    def run(self, feed_dict):
        """Computes values of nodes in eval_node_list given computation graph.
        Parameters
        ----------
        feed_dict: list of variable nodes whose values are supplied by user.

        Returns
        -------
        A list of values for nodes in eval_node_list.
        """
        node_to_val_map = dict(feed_dict)
        # Traverse graph in topological sort order and compute values for all nodes.
        topo_order = find_topo_sort(self.eval_node_list)
        """TODO: Your code here"""
        for node in topo_order:
            if node not in node_to_val_map:
                vs = [node_to_val_map[input] for input in node.inputs]
                value = node.op.compute(node, vs)
                node_to_val_map[node] = value
        value_output = [node_to_val_map[node] for node in self.eval_node_list]
        return value_output


def gradients(output_node, node_list):
    """Take gradient of output node with respect to each node in node_list.

    Parameters
    ----------
    output_node: output node that we are taking derivative of.
    node_list: list of nodes that we are taking derivative wrt.

    Returns
    -------
    A list of gradient values, one for each node in node_list respectively.

    """

    # a map from node to a list of gradient contributions from each output node
    node_to_output_grads_list = {}
    # Special note on initializing gradient of output_node as oneslike_op(output_node):
    # We are really taking a derivative of the scalar reduce_sum(output_node)
    # instead of the vector output_node. But this is the common case for loss function.
    node_to_output_grads_list[output_node] = [oneslike_op(output_node)]
    # a map from node to the gradient of that node
    node_to_output_grad = {}
    # Traverse graph in reverse topological order given the output_node that we are taking gradient wrt.
    reverse_topo_order = reversed(find_topo_sort([output_node]))

    """TODO: Your code here"""
    # For every node, we compute them a reversed topology order. Thus,
    # all the other paths have been computed already
    # When we compute the gradient for a specific node,
    # we can also update the gradient for previous computed node
    for node in reverse_topo_order:
        node_to_output_grad[node] = sum_node_list(node_to_output_grads_list[node])
        input_gradient = node.op.gradient(node, node_to_output_grad[node])
        for i in range(len(node.inputs)):
            n = node.inputs[i]
            g = input_gradient[i]
            if n not in node_to_output_grads_list:
                node_to_output_grads_list[n] = [g]
            else:
                node_to_output_grads_list[n].append(g)
    # Collect results for gradients requested.
    grad_node_list = [node_to_output_grad[node] for node in node_list]
    return grad_node_list


##############################
####### Helper Methods #######
##############################
def find_topo_sort(node_list):
    """Given a list of nodes, return a topological sort list of nodes ending in them.

    A simple algorithm is to do a post-order DFS traversal on the given nodes,
    going backwards based on input edges. Since a node is added to the ordering
    after all its predecessors are traversed due to post-order DFS, we get a topological
    sort.

    """
    visited = set()
    topo_order = []
    for node in node_list:
        topo_sort_dfs(node, visited, topo_order)
    return topo_order


def topo_sort_dfs(node, visited, topo_order):
    """Post-order DFS"""
    if node in visited:
        return
    visited.add(node)
    for n in node.inputs:
        topo_sort_dfs(n, visited, topo_order)
    topo_order.append(node)


def sum_node_list(node_list):
    """Custom sum function in order to avoid create redundant nodes in Python sum implementation."""
    from operator import add
    from functools import reduce
    return reduce(add, node_list)