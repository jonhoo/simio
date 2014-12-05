#!/usr/bin/env python2

import sys

# use the parser to generate wtf
import wtf

def log(s):
    print >> sys.stderr, '%s' % (s)

def torender(s):
    print >> sys.stdout, '%s' % (s)

# Special IDs used to catch unconnected output actions
class StaticID:
    ENVIRONMENT = -1

class EnAction:
    def __init__(self, src, an, ty, dest):
        self.aname = an
        self.atype = ty
        self.src = src
        self.dst = dest

    def __repr__(self):
        s = '<EnAction; name: %s, type: %s, src: %d, dst: %d >' \
            % (self.aname, self.atype, self.src, self.dst)
        return s

class SNode:
    def __init__(self, gid, name, obj, ac, ta):
        self.myid = gid
        self.name = name
        self.obj = obj
        self.actions = ac
        self.tasks = ta
        # a map of action names to pairs of (i, j) where i is the destination
        # id and j is the action of the node corresponding to destination id
        self.omap = {}
        self.nbrs = {}

    def conn_output(self, srcac, dstid, dstac):
        if srcac not in self.actions:
            raise ValueError('%s is not an action for %s' % (srcac, self.name))
        assert self.actions[srcac]['atype'] == 'output'

        om = self.omap
        destpair = (dstid, dstac)
        if om.has_key(srcac):
            om[srcac].append(destpair)
        else:
            om[srcac] = [destpair]

        if not self.nbrs.has_key(dstid):
            self.nbrs[dstid] = True

    def getenabled(self):
        '''
        returns list of EnActions. if the atype of the action is 'output', dest
        is the destination id of the enabled output action.
        '''

        actions = self.actions
        tasks = self.tasks

        ret = []
        for ct in tasks:
            action = actions[ct]

            # input actions never have preconditions
            atype = action['atype']
            assert atype != 'input'

            arity = action['arityprec']

            if atype == 'internal':
                assert arity == 0
                if action['prec']():
                    ret.append(EnAction(self.myid, ct, atype, 0))
                    continue

            # must be an output action
            if ct not in self.omap:
                raise ValueError('output %s is not connected?' % (ct))

            oputnbrs = [x[0] for x in self.omap[ct]]
            # -1 because we provide the dest id
            arity -= 1
            for tf in oputnbrs:
                args = [tf] + [0 for i in range(arity)]

                if apply(action['prec'], args):
                    ret.append(EnAction(self.myid, ct, atype, tf))

        return ret

    def namefor(self, myactname, dst):
        for i in self.omap[myactname]:
            if i[0] == dst:
                return i[1]

    def Nbrs(self):
        # special ids
        spec = [-1]
        return filter(lambda x: x not in spec, [x for x in self.nbrs])

class Net:

    def __init__(self):
        self.nodes = {}
        self.actionstash = []

    def addnode(self, i, sn):
        self.nodes[i] = sn

    def addedge(self, srcid, srcaction, dstid, dstaction):
        sn = self.nodes[srcid]
        sn.conn_output(srcaction, dstid, dstaction)
        if dstid == StaticID.ENVIRONMENT:
            return
        sn = self.nodes[dstid]
        assert sn.actions[dstaction]['atype'] == 'input'

    def doenaction(self, ea):

        sn = self.nodes[ea.src]
        action = sn.actions[ea.aname]
        if ea.atype == 'internal':
            assert action['arityeff'] == 0
            action['eff']()

            return

        # must be output action
        arity = action['arityoutput']
        # arity-1 since we provide dest, the rest are dummy args (should not
        # generate them in the parser?)
        args = [ea.dst] + [0 for i in range(arity - 1)]
        output = apply(action['output'], args)
        apply(action['eff'], args)

        # provide the output as input to the appropriate automaton
        if ea.dst == StaticID.ENVIRONMENT:
            log('Output to env: %s' % (str(output)))
            return

        dn = self.nodes[ea.dst]
        inactname = sn.namefor(ea.aname, ea.dst)
        inaction = dn.actions[inactname]
        assert arity == inaction['arityeff']
        args = [ea.src] + [output]
        apply(inaction['eff'], args)

        torender('send %s %s %s' % (sn.name, dn.name, ea.aname))
        torender('recv %s %s %s' % (dn.name, sn.name, inactname))

    def simstarting(self, m):
        n = self.N()
        for i in self.nodes.values():
            i.obj.N = n
            i.obj.weights = {i:i for i in range(n)}
            i.obj.nbrs = i.Nbrs()
            i.obj.markcb = m

    def getenabledall(self):
        return reduce(lambda x, y: x + y, [self.nodes[x].getenabled() for x in self.nodes])

    def step(self):
        if not self.actionstash:
            self.actionstash = self.getenabledall()
        acs = self.actionstash

        if not acs:
            log('no enabled actions')
            return False

        nextaction = acs[0]
        acs = acs[1:]
        # remove all enabled actions from the node that owns nextaction since
        # execution of nextaction may disable the other enabled actions
        acs = filter(lambda x: x.src != nextaction.src, acs)

        self.actionstash = acs
        self.doenaction(nextaction)

        return True

    def N(self):
        n = len(self.nodes)
        # print warning if fishy stuff
        eyes = [x.obj.i for x in self.nodes.values()]
        ns = range(n+1)
        for i in eyes:
            if i not in ns:
                print >> sys.stderr, '*Warning: missing an ID'

        return n

if __name__ == '__main__':

    autos = {}
    chan = wtf.allclasses['Channel']
    n = Net()
    no = chan()
    no.init()
    n.addnode(no.i, SNode(0, 'Channel-0', no, no.actions(), no.tasks()))
    autos[no.i] = no

    no = chan()
    no.init()
    n.addnode(no.i, SNode(1, 'Channel-1', no, no.actions(), no.tasks()))
    autos[no.i] = no

    assert autos[0].i == 0
    assert autos[1].i == 1

    for o, i in autos[0].connectout.iteritems():
        n.addedge(autos[0].i, o, 1, i)
    for o in autos[1].connectout:
        n.addedge(autos[1].i, o, StaticID.ENVIRONMENT, 'dur')

    n.simstarting(lambda x: torender(x))
    print >> sys.stderr, n.getenabledall()
    print 'sending message...'
    n.nodes[0].actions['send']['eff'](StaticID.ENVIRONMENT, 'duh hello!')
    print >> sys.stderr, n.getenabledall()
    n.step()
    print >> sys.stderr, n.getenabledall()
    n.step()
    print >> sys.stderr, n.getenabledall()
