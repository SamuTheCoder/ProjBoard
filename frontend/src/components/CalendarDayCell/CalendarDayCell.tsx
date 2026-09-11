import type { TaskResponse } from "../../types/task";

import { CalendarTaskChip } from "../CalendarTaskChip/CalendarTaskChip";

import "./CalendarDayCell.css";

type CalendarDayCellProps = {
    date: Date;

    tasks: TaskResponse[];

    isCurrentMonth: boolean;
    isToday: boolean;
    isSelected: boolean;

    onSelect: (date: Date) => void;
    onTaskClick: (task: TaskResponse) => void;
};

export function CalendarDayCell({
    date,
    tasks,
    isCurrentMonth,
    isToday,
    isSelected,
    onSelect,
    onTaskClick,
}: CalendarDayCellProps) {
    return (
        <div
            className={[
                "calendar-day-cell",
                !isCurrentMonth ? "outside-month" : "",
                isSelected ? "selected" : "",
            ]
                .filter(Boolean)
                .join(" ")}
            onClick={() => onSelect(date)}
        >
            <div className="calendar-day-number">
                <span className={isToday ? "today" : ""}>{date.getDate()}</span>
            </div>

            <div className="calendar-day-tasks">
                {tasks.slice(0, 3).map((task) => (
                    <CalendarTaskChip
                        key={task.task_id}
                        name={task.task_name}
                        priority={task.priority}
                        onClick={() => onTaskClick(task)}
                    />
                ))}

                {tasks.length > 3 && (
                    <span className="calendar-more-tasks">
                        +{tasks.length - 3} more
                    </span>
                )}
            </div>
        </div>
    );
}
