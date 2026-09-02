"""
Central mutable application state.

AURA keeps one 'current' atmospheric picture in memory (current demo scenario,
and an optional what-if rainfall override). Every risk/zone/map/alert/assistant
endpoint reads from this single source of truth so the whole application reacts
consistently when the scenario or simulation changes.
"""

class AppState:
    def __init__(self):
        self.scenario = "NORMAL"
        self.rainfall_override_mm = None  # set by the what-if simulator, cleared on scenario switch

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        self.rainfall_override_mm = None

    def set_rainfall_override(self, mm: float):
        self.rainfall_override_mm = mm


state = AppState()
