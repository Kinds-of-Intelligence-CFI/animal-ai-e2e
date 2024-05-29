from shared import run_behaviour_in_aai, backwards_action, forwards_action, nothing_action

def test_basic_success():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testUnmergedArenas.yml",
        0.8,
        lambda _ : forwards_action,
    )

def test_basic_fail():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testUnmergedArenas.yml",
        -1,
        lambda _ : nothing_action,
    )

def test_items():
    pass

def test_blackout():
    pass

def test_training():
    pass
