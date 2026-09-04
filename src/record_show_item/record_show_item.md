purpose: get one record item by id, with kind and state decoded from its labels
signature: record_show_item(item_id: str) -> dict
inputs: item_id: existing id
outputs: {'id','kind','title','owner','state','parent','sheet'} where sheet is the description text ('' if none)
side effects: runs the external record tool via record_run; raises RecordError for an unknown id
work item id: 0001-4-record_show_item-code
