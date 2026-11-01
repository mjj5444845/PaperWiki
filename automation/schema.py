"""Strict output schema for a read-only extraction worker; no executable patches."""
def obj(properties):
    return dict(type='object',properties=properties,required=list(properties),additionalProperties=False)
def array(item):return dict(type='array',items=item)
S={'type':'string'}
EVIDENCE=obj({'page':{'type':'integer','minimum':1},'section':S,'quote':S})
FACT=obj({'text':S,'evidence':array(EVIDENCE)})
META=obj({'value':S,'evidence':array(EVIDENCE)})
SCHEMA=obj({
 'metadata':obj({k:META for k in ['title','title_zh','authors','year','venue','doi','arxiv','code']}),
 'field':S,
 'lead':array(FACT),'background':array(FACT),'method':array(FACT),'contributions':array(FACT),
 'datasets':array(FACT),'results':array(FACT),'limitations':array(FACT),
 'concepts':array(obj({'original_term':S,'canonical_name':S,'existing_id':S,'aliases':array(S),
                      'stable':{'type':'boolean'},'prerequisite':{'type':'boolean'},
                      'definition':FACT,'application':FACT})),
 'cites_existing':array(obj({'paper_id':S,'evidence':array(EVIDENCE)})),
 'review':array(S),'checklist':array(obj({'item':{'type':'integer'},'status':{'type':'string','enum':['pass','review','not_applicable']},'reason':S})),
 'publishable':{'type':'boolean'}
})
