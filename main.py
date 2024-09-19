class Week():
    def __init__(self, name: str, load_focus: str) -> None:
        self.name: str = name
        self.load_focus: str = load_focus
        self.days: list[Day] = [Day() for _ in range(0, 7)]

    def __str__(self) -> str:
        week_str = f"Week: {self.name} (Load Focus: {self.load_focus})\n"
        week_str += "Days:\n"
        for i, day in enumerate(self.days):
            week_str += f"  Day {i+1}:\n"
            week_str += str(day)  # Use Day's __str__ method
        return week_str

class Day():
    def __init__(self) -> None:
        self.activities: list[Activity] = [] 

    def __str__(self) -> str:
        if not self.activities:
            return "    Rest Day\n"
        day_str = ""
        for activity in self.activities:
            day_str += f"    {str(activity)}\n"  # Use Activity's __str__ method
        return day_str

class Activity():
    def __init__(self, locked: bool, name: str, load_focus: str, time_interval: tuple[int], intensity_interval: tuple[float], repetions: int = 1, repetion_time: int = 0, work_to_rest: int = 0) -> None:
        self.isLocked: bool = locked
        self.name: str = name
        self.load_focus: str = load_focus
        self.repetions: int = repetions
        self.repetion_time: int = repetion_time
        self.rest_to_work: int = work_to_rest
        self.time_interval: tuple[int] = time_interval
        self.intensity_interval: tuple[float] = intensity_interval

    def __str__(self) -> str:
        return (f"Activity: {self.name} (Locked: {'Yes' if self.isLocked else 'No'})\n"
                f"      Load Focus: {self.load_focus}\n"
                f"      Time Interval: {self.time_interval} mins\n"
                f"      Intensity: {self.intensity_interval}\n"
                f"      Repetitions: {self.repetions}, Repetition Time: {self.repetion_time} mins\n"
                f"      Work-to-Rest Ratio: 1:{self.rest_to_work}")

class Person():
    def __init__(self, vo2max: float, endurance: int, hill_endurance: int, hill_strength: int) -> None:
        self.vo2max: float = vo2max
        self.endurance: int = endurance
        self.hill_endurance: int = hill_endurance
        self.hill_strength: int = hill_strength

class Optimizer():
    def __init__(self, recovery_threshold: float = 54.0, z2_threshold: float = 27.0, recovery_base_threshold: float = 20.0, recovery_rate: float = 1.3, intensity_factor: float = 3.0):
        self.recovery_threshold: float = recovery_threshold
        self.z2_threshold: float = z2_threshold
        self.recovery_base_threshold: float = recovery_base_threshold

        self.recovery_rate: float = recovery_rate
        self.intensity_factor: float = intensity_factor

def get_next_week(weeks: list[Week], optimizer: Optimizer) -> Week:
    new_week: Week = weeks[-1]

    load_counts = {}

    for week in weeks:
        for day in week.days:
            for activity in day.activities:
                if activity.load_focus in load_counts:
                    load_counts[activity.load_focus] += 1
                else:
                    load_counts[activity.load_focus] = 1

    if "recovery" not in load_counts:
        new_week.load_focus = "recovery"
    elif "anaerobic" not in load_counts:
        new_week.load_focus = "anaerobic"
    elif load_counts.get("high_aerobic", 0) > load_counts.get("low_aerobic", 0):
        new_week.load_focus = "low_aerobic"
    else:
        new_week.load_focus = "high_aerobic"

    for idx, day in enumerate(new_week.days):
        for activity in day.activities:
            if not activity.isLocked:

                total_load: float = 0
                if idx == 0:
                    pass
                else:
                    for idx2, other_day in enumerate((weeks[2].days + new_week.days)[:7]):
                        for other_activity in other_day.activities:
                            if other_activity.repetions > 1:
                                total_time = other_activity.repetions * other_activity.repetion_time * (1+other_activity.rest_to_work)
                            else:
                                total_time = (other_activity.time_interval[0] + other_activity.time_interval[1]) / 2.0
                            
                            base_intensity: float = (other_activity.intensity_interval[0] + other_activity.intensity_interval[1]) / 2.0
                            adjusted_intensity: float = base_intensity ** optimizer.intensity_factor

                            total_load += total_time * adjusted_intensity * ((7-idx2) ** -optimizer.recovery_rate)

                new_activity: Activity = get_activity(new_week.load_focus, total_load, optimizer)
                activity = new_activity

    return new_week

def get_activity(focus: str, load: float, optimizer: Optimizer) -> Activity:
    if focus == "recovery":
        if load <  optimizer.recovery_base_threshold:
            return Activity(locked=False, name="base", load_focus="low_aerobic", time_interval=(40, 60), intensity_interval=(0.65, 0.75))
        if load <  optimizer.z2_threshold:
            return Activity(locked=False, name="z2", load_focus="low_aerobic", time_interval=(50, 70), intensity_interval=(0.6, 0.7))
        if load <  optimizer.recovery_threshold:
            return Activity(locked=False, name="recovery", load_focus="low_aerobic", time_interval=(20, 40), intensity_interval=(0.6, 0.7))
        return None

if __name__ == "__main__":
    player1_optimizer = Optimizer()
    
    player1_weeks = [
        Week("Base", "high_aerobic"),
        Week("Endurance", "low_aerobic"),
        Week("Speed", "anaerobic"),
        Week("Recovery", "recovery")
    ]

    player1_weeks[0].days[0].activities = [
        Activity(locked=False, name="Long Run", load_focus="low_aerobic", time_interval=(60, 90), intensity_interval=(0.7, 0.7))
    ]
    player1_weeks[0].days[1].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 80), intensity_interval=(0.6, 0.8)),
        Activity(locked=True, name="O-tech", load_focus="high_aerobic", time_interval=(55, 70), intensity_interval=(0.7, 0.8))
    ]
    player1_weeks[0].days[2].activities = [
        Activity(locked=True, name="Academy", load_focus="high_aerobic", time_interval=(50, 70), intensity_interval=(0.8, 0.85))
    ]
    player1_weeks[0].days[3].activities = [
        Activity(locked=False, name="Recovery", load_focus="low_aerobic", time_interval=(20, 40), intensity_interval=(0.5, 0.6))
    ]
    player1_weeks[0].days[4].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 75), intensity_interval=(0.5, 0.65))
    ]
    player1_weeks[0].days[5].activities = [
        Activity(locked=False, name="HIIT", load_focus="anaerobic", time_interval=(8, 8), intensity_interval=(0.9, 0.95), repetions=8, repetion_time=1, work_to_rest=1)
    ]
    player1_weeks[0].days[6].activities = []


    player1_weeks[1].days[0].activities = [
        Activity(locked=False, name="Z2 Run", load_focus="low_aerobic", time_interval=(50, 70), intensity_interval=(0.6, 0.7))
    ]
    player1_weeks[1].days[1].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 80), intensity_interval=(0.6, 0.8)),
        Activity(locked=True, name="O-tech", load_focus="high_aerobic", time_interval=(55, 70), intensity_interval=(0.7, 0.8))
    ]
    player1_weeks[1].days[2].activities = [
        Activity(locked=True, name="Academy", load_focus="high_aerobic", time_interval=(50, 70), intensity_interval=(0.8, 0.85))
    ]
    player1_weeks[1].days[3].activities = []
    player1_weeks[1].days[4].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 75), intensity_interval=(0.5, 0.65))
    ]
    player1_weeks[1].days[5].activities = [
        Activity(locked=False, name="Long Run", load_focus="low_aerobic", time_interval=(60, 90), intensity_interval=(0.7, 0.7))
    ]
    player1_weeks[1].days[6].activities = [
        Activity(locked=False, name="Recovery", load_focus="low_aerobic", time_interval=(20, 40), intensity_interval=(0.5, 0.6))
    ]

    player1_weeks[2].days[0].activities = [
        Activity(locked=False, name="HIIT", load_focus="anaerobic", time_interval=(8, 8), intensity_interval=(0.9, 0.95), repetions=8, repetion_time=1, work_to_rest=1)
    ]
    player1_weeks[2].days[1].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 80), intensity_interval=(0.6, 0.8)),
        Activity(locked=True, name="O-tech", load_focus="high_aerobic", time_interval=(55, 70), intensity_interval=(0.7, 0.8))
    ]
    player1_weeks[2].days[2].activities = [
        Activity(locked=True, name="Academy", load_focus="high_aerobic", time_interval=(50, 70), intensity_interval=(0.8, 0.85))
    ]
    player1_weeks[2].days[3].activities = []
    player1_weeks[2].days[4].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 75), intensity_interval=(0.5, 0.65))
    ]
    player1_weeks[2].days[5].activities = [
        Activity(locked=False, name="Hill Sprints", load_focus="anaerobic", time_interval=(12, 20), intensity_interval=(0.90, 0.95), repetions=12, repetion_time=0.2, work_to_rest=2)
    ]
    player1_weeks[2].days[6].activities = [
        Activity(locked=False, name="Recovery", load_focus="low_aerobic", time_interval=(20, 40), intensity_interval=(0.5, 0.6))
    ]

    player1_weeks[3].days[0].activities = [
        Activity(locked=False, name="Base Run", load_focus="low_aerobic", time_interval=(40, 60), intensity_interval=(0.7, 0.7))
    ]
    player1_weeks[3].days[1].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 80), intensity_interval=(0.6, 0.8)),
        Activity(locked=True, name="O-tech", load_focus="high_aerobic", time_interval=(55, 70), intensity_interval=(0.7, 0.8))
    ]
    player1_weeks[3].days[2].activities = [
        Activity(locked=True, name="Academy", load_focus="high_aerobic", time_interval=(50, 70), intensity_interval=(0.8, 0.85))
    ]
    player1_weeks[3].days[3].activities = [
        Activity(locked=False, name="Recovery", load_focus="low_aerobic", time_interval=(20, 40), intensity_interval=(0.5, 0.6))
    ]
    player1_weeks[3].days[4].activities = [
        Activity(locked=True, name="Academy", load_focus="low_aerobic", time_interval=(60, 75), intensity_interval=(0.5, 0.65))
    ]
    player1_weeks[3].days[5].activities = [
        Activity(locked=False, name="Z2 Run", load_focus="low_aerobic", time_interval=(50, 70), intensity_interval=(0.60, 0.70))
    ]
    player1_weeks[3].days[6].activities = []

    next_week = get_next_week(player1_weeks, player1_optimizer)

    print(next_week)