from laya import Router
from laya_ai.categories import categories
import json


# TODO: Seperate out downloading model from runtime usage (allow & prevent downloading model)
#
# # Or specify cache_dir when loading
# agent = laya.load(
#    "convaiinnovations/laya",
#    cache_dir="/specific/path"
#)#
#If you want checkpoints as standalone directories you can version, ship in a container, or air-gap manually:
# # Snapshot just one checkpoint into its own folder
# huggingface-cli download convaiinnovations/laya \
#     --include "multilingual/*" \
#     --local-dir ./models/laya-multilingual \
#     --local-dir-use-symlinks False
# Then load from the local path instead of the Hub — no network at all:
# import laya

# agent_ml = laya.load("./models/laya-multilingual")
# 
# 


router = Router()

# Get inbox tasks (as 'state'(s))


tasks = ["Submit homestead paperwork", "Find vet for shadow", "Buy milk", "clean up porch", "Winterize houseplants", "Plan life"]

questions = {
    "priority": {
        "type": "choice",
        "instructions": "What is the relative priority of this task?",
        "criteria": {
            "p1": "This is the most important item.",
            "p2": "Not the top priority, but needs to be done.",
            "p3": "Good thing to help improve things.",
            "p4": "Get to it when there is free time.",
        }
    },
    "category": categories,
    "is-atomic": {
        "type": "noul",
        "instructions": "Can this task be done in one step, at once without further follow ups?"
    }
}


for task in tasks:
    result = router.predict(task, questions)
    print("## TASK: ", task)
    print(json.dumps(result, indent=4))
