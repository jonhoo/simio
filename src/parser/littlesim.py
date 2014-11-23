#!/usr/bin/env python

import wtf

def getenabled(a):

    ac = a.actions()

    for ct in a.tasks():
        action = ac[ct]

        # these are fake node identifiers -- the simulator obviously should use
        # real ids. the behavior of an automaton's actions may depend on the
        # sending or receiving node's id
        receiverid = 42
        senderid = 31337

        # input actions never have preconditions
        atype = action['atype']
        if atype == 'input':
            continue
        elif atype == 'output':
            tf = receiverid
        else:
            tf = senderid

        # the arity matters because we allow action to send multiple values.
        # maybe this is a mistake?
        arity = action['arityprec']

        # the first argument to any of the action methods (eff, prec, output)
        # depends on the action type (atype):
        #   output    - the id of the receiving node
        #   input     - the id of the sending node
        #   internal  - no assumed arg (internal actions never send/receive
        #       values?)
        assert arity > 0
        arity -= 1
        args = [tf] + [0 for i in range(arity)]

        if apply(action['prec'], args):
            return ct

def sendmessage(a):
    # have node 42 send a message on the channel
    ac = a.actions()
    fromnode = 42
    ac['send']['eff'](fromnode, 'hello world!')

def recmessage(a):
    # use the 'output' method of the action to get the actual value that the
    # action should send
    # since this is an output action, the first argument should be the
    # destination node.

    # XXX argument is useless for output action -- just a part of original
    # notation
    ac = a.actions()
    fromnode = 43
    arg = None
    m = ac['receive']['output'](fromnode, arg)

    # now cycle the automatons state -- execute the effect method
    ac['receive']['eff'](fromnode, arg)

    return m

nc = wtf.allclasses['Channel']()

nc.init()
ea = getenabled(nc)
if ea:
    print 'found enabled action:', ea
else:
    print 'no enabled action'

print 'sending the channel a message'
sendmessage(nc)

ea = getenabled(nc)
if ea:
    print 'found enabled action:', ea
else:
    print 'no enabled action'

m = recmessage(nc)
print 'received message:', m
