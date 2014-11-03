#!/usr/bin/env python

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
    def setname(self, l):
        self.name = l

class Parser:

    def __init__(self):
        self.state = states.START
        self.auto = newauto()

    def dump(self):
        print 'this will print an automaton soon'

        print self.auto
        print 'trans'
        for i in self.auto['trans']:
            print i

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
        self.auto['sigin'].append(l)

    def ppsigint(self, l):
        self.auto['sigint'].append(l)

    def ppsigout(self, l):
        self.auto['sigout'].append(l)

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

    print 'done'
