class Week():
    def __init__(self, name: str, load_focus: str) -> None:
        self.name: str = name
        self.load_focus: str = load_focus
        self.days: list[Day] = []

class Day():
    def __init__(self) -> None:
        self.activites: list[Activity] = [] 

class Activity():
    def __init__(self, locked: bool, name: str, load_focus: str, time_interval: tuple[int], intensity_interval: tuple[float], repetions: int = 0, repetion_time: int = 0) -> None:
        self.isLocked: bool = locked
        self.name: str = name
        self.load_focus: str = load_focus
        self.repetions: int = repetions
        self.repetion_time: int = repetion_time
        self.time_interval: tuple[int] = time_interval
        self.intensity_interval: tuple[float] = intensity_interval

class Person():
    def __init__(self, vo2max: float, endurance: int, hill_endurance: int, hill_strength: int) -> None:
        self.vo2max: float = vo2max
        self.endurance: int = endurance
        self.hill_endurance: int = hill_endurance
        self.hill_strength: int = hill_strength

class Optimizer():
    def __init__(self, recovery_threshold: float = 100.0, z2_threshold: float = 120.0, recovery_base_threshold: float = 220.0):
        self.recovery_threshold: float = recovery_threshold
        self.z2_threshold: float = z2_threshold
        self.recovery_base_threshold: float = recovery_base_threshold

def get_next_week(weeks: list[Week], person: Person, optimizer: Optimizer) -> Week:
    new_week: Week = weeks[0]

    load_counts = {}

    for week in weeks:
        for day in week.days:
            for activity in day.activites:
                load_counts[activity.load_focus] += 1

    if "recovery" not in load_counts:
        new_week.load_focus = "recovery"
    elif "anaerobic" not in load_counts:
        new_week.load_focus = "anaerobic"
    elif load_counts.get("high_aerobic", 0) > load_counts.get("low_aerobic", 0):
        new_week.load_focus = "low_aerobic"
    else:
        new_week.load_focus = "high_aerobic"

    for idx, day in enumerate(new_week.days):
        for activity in day.activites:
            if not activity.isLocked:

                total_load: float = 0
                if idx == 0:
                    pass
                else:
                    for other_day in new_week.days[:idx]:
                        for other_activity in other_day.activites:
                            if other_activity.repetions > 1:
                                total_load += float(other_activity.repetion_time * other_activity.repetions) * (
                                                other_activity.intensity_interval[0] + other_activity.intensity_interval[1]) / 2.0
                            else:
                                total_load += float(other_activity.time_interval[0] + other_activity.time_interval[1]) / 2.0 * (
                                                other_activity.intensity_interval[0] + other_activity.intensity_interval[1]) / 2.0
                total_load /= len(new_week.days[:idx])

                new_activity: Activity = get_activity(person, new_week.load_focus, total_load, optimizer)

                if new_activity:
                    activity = new_activity

    return new_week

def get_activity(person: Person, focus: str, load: float, optimizer: Optimizer) -> Activity:
    if focus == "recovery":
        if load < person.endurance / optimizer.recovery_base_threshold:
            return Activity(locked=False, name="base", load_focus="aerobic", time_interval=(40, 60), intensity_interval=(0.65, 0.75))
        if load < person.endurance / optimizer.z2_threshold:
            return Activity(locked=False, name="z2", load_focus="aerobic", time_interval=(50, 70), intensity_interval=(0.6, 0.7))
        if load < person.endurance / optimizer.recovery_threshold:
            return Activity(locked=False, name="recovery", load_focus="aerobic", time_interval=(20, 40), intensity_interval=(0.6, 0.7))
        return None