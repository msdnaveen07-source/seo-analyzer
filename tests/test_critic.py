from backend.agent.critic import SelfCritiqueEngine

def test_critic_title_validation():
    critic = SelfCritiqueEngine()
    
    # 54 characters, includes keyword near start
    valid_title = "SEO Optimization Guide - Master On-Page SEO Practices"
    res = critic.critique_title_fix(valid_title, "SEO Optimization")
    assert res["valid"] is True

    # Short title
    short_title = "Short Title"
    res_short = critic.critique_title_fix(short_title, "SEO Optimization")
    assert res_short["valid"] is False
