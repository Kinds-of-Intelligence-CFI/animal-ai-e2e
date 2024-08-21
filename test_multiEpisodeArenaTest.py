from shared import run_behaviour_in_aai, backwards_action, forwards_action, nothing_action

# If we include MergeNextArena both arenas are included in the episode

def test_should_merge_if_merge_flag_included():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testMergedArenas.yml",
        1.6,
        lambda r : backwards_action if r > 0 else forwards_action
    )

# Failure scenarios should not roll into a merged arena

def test_should_skip_next_merged_arena_if_fails_from_lava():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testFailArenas.yml",
        0.895,
        lambda _ : forwards_action,
        forwards_action
    )

def test_should_skip_next_merged_arena_if_fails_from_timeout():
    run_behaviour_in_aai(
        r".\animal-ai-e2e\testConfigs\testFailArenas.yml",
        0.895,
        lambda _ : forwards_action,
        nothing_action
    )
