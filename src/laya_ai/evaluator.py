from laya import Router
import json

router = Router()

state = "Hi, we were billed twice! for the same service. Help resolve this, otherwise I will cancel! Take a look at my cat!"

questions = {
    "departments": { 
        "type": "choice",
        "instructions": "Which department should handle this issue?",
        "criteria": {
            "billing": "invoices, payments, refunds",
            "technical": "bugs, outages, system errors",
            "other": "everything else"
        }
    },
    "urgency": {
    "type": "score",
        "instructions": "How urgent is this issue?",
        "criteria": [
            "nice-to-have",
            "not-urgent",
            "soon",
            "blocking",
        ]
    },
    "churn_risk": {
        "type": "noul",
        "instructions": "Does the user threaten to cancel their subscription or leave?"
    }
}
result = router.predict(state, questions)

print(json.dumps(result, indent=4))
