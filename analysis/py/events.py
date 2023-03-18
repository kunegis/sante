#
# Information about events, in particular the name.  Events are represented as
# strings. 
#

import re
import sys

class _Data:

    texts_by_event= None

    tags= set()

    subevents_by_aggregate_event= None

#
# Text that corresponds to an event, except when the event has no text. 
#
def text_for_event(event):
    if event[0] == '#':
        raise Exception('Tags have no text')
    if event[0] == '$':
        raise Exception('Tracker events have no text')
    init_data()
    ret= _Data.texts_by_event[event]
    return ret

def label_for_event(event):
    if event[0] == '#':
        return event
    if event[0] == '$':
        return event
    text= text_for_event(event)
    return f'{event} {text}'

def get_ylabel(event, typ):
    normalize= get_normalize(event, typ)
    if event == '$steps':
        ret= 'Steps'
    elif event == '$distance':
        ret= 'Distance'
    elif re.compile('[({][A-Za-zα-ω][})]').fullmatch(event):
        ret= 'Intensity sum'
    elif event == '(&)':
        ret= 'Characters'
    elif event == '#all':
        ret= 'Medical products'
    else:
        ret= 'Count'
    if normalize:
        ret += ' ' + 'per day'
    if event == '$distance':
        ret += ' ' + '[m]';
    return ret

# Whether the event needs normalization
def get_normalize(event, typ):
    if event[0] == '$' or event == '(&)' or event == '{A}' or event == '#all':
        if typ[0] == 'd':
            if typ == 'dz':
                return True
            else:
                return False
        else:
            return True
    return False
    
def check_tag(tag):
    init_data()
    if not tag in _Data.tags:
        raise Exception(f'Invalid tag #{tag}: tag must appear in LEGEND')

def aggregate_events():
    init_data()
    return list(_Data.subevents_by_aggregate_event.keys())

def subevents(event):
    init_data()
    return _Data.subevents_by_aggregate_event[event]
    
def init_data():
    if not _Data.texts_by_event:
        _Data.texts_by_event= {}
        _Data.subevents_by_aggregate_event= {}

        file= open('sante/LEGEND', 'r')

        while True:
            line= file.readline()
            if not line:  break

            #
            # (*) and {*}
            #
            m= re.compile('^([({][^)}]*[})]) ((\w| |-)*)').match(line)
            if m:
                event= m.group(1)
                text = m.group(2)
                text= re.sub('\s*$', '', text)
                _Data.texts_by_event[event]= text
                if event[0] == '(':
                    _Data.texts_by_event[f'[{event[1:len(event)-1]}]']= f'Risky activity for {text}'

            #
            # #tags
            #
            m= re.compile('#(\w+)(\W|$)').match(line)
            if m:
                tag= m.group(1)
                _Data.tags.add(tag)

            #
            # @
            #
            m= re.compile('^@([A-Z])(.*)').match(line)
            if m:
                measure= m.group(1)
                description= m.group(2)
                m= re.compile('^\s*([\w ]+\w)').match(description)
                if not m:
                    raise Exception(f'Invalid measurement legend: {line}')
                text= m.group(1)
                event= f'@{measure}'
                _Data.texts_by_event[event]= text

            #
            # $tracker
            #
            m= re.compile('^\\$([a-z]+)\s+(\w.*\w)\s*$').fullmatch(line)
            if m:
                event= f'${m.group(1)}'
                text= m.group(2)
                _Data.texts_by_event[event]= text

            #
            # Subevents by aggregate events 
            #
            m= re.compile('([{][A-Z][}])').match(line)
            if m:
                parent_event= m.group(1)
                if parent_event == '{A}':  continue
                subevents= []
                m= re.compile('\([^()]+\)').findall(line)
                for e in m:
                    subevents.append(e)
                _Data.subevents_by_aggregate_event[parent_event]= subevents

        file.close()
        
