#!/usr/bin/env python

import hashlib
import sys

def lump(pre, post):
    return [pre + i for i in post]

class states:
    START   =  0
    SIGINP  =  1
    SIGOUTP =  2
    TRANPRE =  3
    TRANOUT =  4
    TRANEFF =  5
    NAME    =  6
    STATE   =  7
    TASKS   =  8
    TRANNAM =  9
    SIGINT  =  10

def newauto():
    r = {'sigin': [], 'sigint': [], 'sigout': [], 'trans': [], 'state': [], 'tasks':[]}

    return r

class Tran:

    def __init__(self):
        self.pres = []
        self.effs = []
        self.out = []
        self.name = 'unknown'

    def __repr__(self):
        ret = '<Tran "%s" ' % (self.name)
        ret += 'Precondition: '
        ret += ';'.join(self.pres)
        ret += ' Output: '
        ret += ';'.join(self.out)
        ret += ' Effects: '
        ret += ';'.join(self.effs)
        ret += '>'

        return ret

    def addpre(self, l):
        self.pres.append(l)
    def addeff(self, l):
        self.effs.append(l)
    def addout(self, l):
        self.out.append(l)

    def prpre(self, idts):
        if not self.pres:
            print '\t'*idts + 'return False'

        for i in self.pres:
            print '\t'*idts + i

    def preff(self, idts):
        if not self.effs:
            print '\t'*idts + 'pass'

        for i in self.effs:
            print '\t'*idts + i

    def prout(self, idts):
        # outputs can be omitted
        if not self.out:
            #print '\t'*idts + 'raise Exception("no imp")'
            print '\t'*idts + 'return None'

        for i in self.out:
            print '\t'*idts + i

    def setname(self, l):
        self.name = l

class Parser:

    def __init__(self):
        self.state = states.START
        self.auto = newauto()

    def addtoret(self, ntd, idts):
        print '\t'*idts + 'd = {',
        for k in ntd:
            print '"' + k + '": %s,' % (ntd[k]),

        print '}'
        print '\t'*idts + 'ret.append(d)'

    def dump(self):
        get = lambda x: self.auto[x]

        print 'class %s:' % (get('name'))
        print
        print '\tdef __init__(self):'
        print '\t\tpass'
        print
        print '\tdef init(self):'
        print ''.join(['\t\t' + i + '\n' for i in get('state')])
        print
        print '\tdef actions(self):'
        print '\t\tret = []'
        for t in get('trans'):
            prec, arity = self.protoprint(t, 'prec', 2)
            ntd = {'name': '"' + t.name + '"', 'prec': prec, 'arityprec': arity}
            t.prpre(3)

            eff, arity = self.protoprint(t, 'eff', 2)
            ntd['eff'] = eff
            ntd['arityeff'] = arity
            t.preff(3)

            op, arity = self.protoprint(t, 'output', 2)
            ntd['output'] = op
            ntd['arityoutput'] = arity
            t.prout(3)

            self.addtoret(ntd, 2)

        print '\t\treturn ret'

    def enterstate(self, s):
        if s == states.SIGINP:
            pass
        elif s == states.SIGOUTP:
            pass
        elif s == states.TRANPRE:
            pass
        elif s == states.TRANOUT:
            pass
        elif s == states.TRANEFF:
            pass
        elif s == states.NAME:
            pass

    def go(self, f):

        for line in f.readlines():

            line = line.strip()
            if line:
                out = self.parse(line)

        self.dump()

    def leavestate(self, s):
        pass

    def parse(self, l):

        statedict = { \
                     states.START   : self.ppnone,
                     states.SIGINP  : self.ppsigin,
                     states.SIGOUTP : self.ppsigout,
                     states.SIGINT  : self.ppsigint,
                     states.TRANPRE : self.pptranpre,
                     states.TRANOUT : self.pptranout,
                     states.TRANEFF : self.pptraneff,
                     states.NAME    : self.ppname,
                     states.STATE   : self.ppstate,
                     states.TASKS   : self.pptasks,
                     states.TRANNAM : self.pptrannam,
                     }

        if l and l[0] == '#':
            return None

        s = self.nextstate(l)

        if s:
            self.leavestate(self.state)
            self.state = s
            self.enterstate(self.state)
            return

        f = statedict[self.state]
        return f(l)

    def ppname(self, l):
        self.auto['name'] = l

    def ppnone(self, l):
        pass

    def ppsigin(self, l):
        # strip parens and args from sigs
        self.auto['sigin'].append(l.split('(')[0])

    def ppsigint(self, l):
        self.auto['sigint'].append(l.split('(')[0])

    def ppsigout(self, l):
        self.auto['sigout'].append(l.split('(')[0])

    def pptranpre(self, l):
        self.auto['trans'][-1].addpre(l)

    def pptranout(self, l):
        self.auto['trans'][-1].addout(l)

    def pptraneff(self, l):
        self.auto['trans'][-1].addeff(l)

    def ppstate(self, l):
        self.auto['state'].append(l)

    def pptasks(self, l):
        self.auto['tasks'].append(l)

    def pptrannam(self, l):
        self.auto['trans'].append(Tran())
        self.auto['trans'][-1].setname(l)

    def protoprint(self, t, ty, idts):
        '''
        prints the prototype with the correct argument (as needed by the
        simulator) and returns the name of the method for inclusion in the list
        of actions.

        ty is the type: it is one of prec, eff, output (precondition, effect,
        and output respectively)
        '''

        if ty not in ['prec', 'eff', 'output']:
            raise ValueError('unknown transition type %s' % (ty))

        get = lambda x: self.auto[x]
        n =  t.name
        lit =  n.split('(')[0]
        args = ''.join(''.join(n.split('(')[1:]).split(')')).split(',')
        sigins = get('sigin')
        sigints = get('sigint')
        sigouts = get('sigout')

        arity = len(args)

        if lit in sigins:
            args.insert(0, 'fr')
            arity += 1
        elif lit in sigouts:
            args.insert(0, 'to')
            arity += 1

        #hs = hashlib.md5(lit).hexdigest()
        #print '\t'*idts + 'def %s_%s%s:' % (lit, hs, ''.join(args))
        lit = '%s_%s' % (lit, ty)
        print '\t'*idts + 'def %s(%s):' % (lit, ','.join(args))

        return lit, arity

    def nextstate(self, l):

        keywords = ['Name', 'State', 'Tasks'] + \
            lump('Signature-', ['Input', 'Output', 'Internal']) + \
            lump('Transition-', ['Name', 'Effect', 'Output', 'Precondition'])
        dstate = [states.NAME, \
                  states.STATE, \
                  states.TASKS, \
                  states.SIGINP, \
                  states.SIGOUTP, \
                  states.SIGINT, \
                  states.TRANNAM, \
                  states.TRANEFF, \
                  states.TRANOUT, \
                  states.TRANPRE, \
                  ]

        d = zip(keywords, dstate)

        for k, v in d:
            if l.startswith(k + ':'):
                return v

if __name__ == '__main__':

    p = Parser()
    with open('test.txt', 'r') as f:
        p.go(f)

    print >> sys.stderr, 'done'
