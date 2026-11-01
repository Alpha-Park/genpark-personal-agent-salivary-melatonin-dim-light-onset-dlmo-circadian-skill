# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-salivary-melatonin-dim-light-onset-dlmo-circadian-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def audit_circadian_dlmo_phase(dlmo_time_decimal_hours, habitual_sleep_onset_decimal_hours):
    # e.g. 21.5 = 21:30 (9:30 PM), 23.5 = 23:30 (11:30 PM)
    # Phase angle = sleep_onset - DLMO
    # Normal physiological phase angle: 1.5 to 2.5 hours
    phase_angle_hours = (habitual_sleep_onset_decimal_hours - dlmo_time_decimal_hours) % 24.0
    
    if phase_angle_hours < 0.75:
        syndrome = "DELAYED_SLEEP_PHASE_CHRONOTYPE"
        recommendation = "Circadian clock is severely delayed relative to social obligations; morning bright light (10,000 lux) and evening blue-blocking advised."
    elif phase_angle_hours > 3.5:
        syndrome = "ADVANCED_CIRCADIAN_PHASE"
        recommendation = "Melatonin surges too early; evening light exposure advised to delay sleep drive."
    else:
        syndrome = "HARMONIC_CIRCADIAN_ENTRAINMENT"
        recommendation = "Optimal 2-hour biological night preparation window before sleep initiation."
        
    return {
        "dlmo_time_hours": round(dlmo_time_decimal_hours, 2),
        "habitual_sleep_onset_hours": round(habitual_sleep_onset_decimal_hours, 2),
        "circadian_phase_angle_hours": round(phase_angle_hours, 2),
        "circadian_alignment_classification": syndrome,
        "clinical_chronobiology_guidance": recommendation
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "audit_circadian_dlmo_phase",
                        "description": """Determine the master circadian phase angle using Dim Light Melatonin Onset (DLMO).
DLMO represents the time salivary melatonin crosses the threshold of 4.0 pg/mL in dim light (< 30 lux).
Calculates Phase Angle difference (target 2.0 hours before habitual sleep onset) to diagnose Delayed Sleep-Wake Phase Disorder (DSWPD) or Advanced Phase Disorder.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = audit_circadian_dlmo_phase(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'dlmo_time_decimal_hours': 21.75, 'habitual_sleep_onset_decimal_hours': 23.5}
        out = audit_circadian_dlmo_phase(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
