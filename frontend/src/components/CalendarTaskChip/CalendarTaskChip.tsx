import "./CalendarTaskChip.css";

type CalendarTaskChipProps = {
    name: string;
    priority: number;
    onClick?: () => void;
};

export function CalendarTaskChip({
    name,
    priority,
    onClick,
}: CalendarTaskChipProps) {
    return (
        <button
            type="button"
            className={`calendar-task-chip calendar-priority-${priority}`}
            onClick={(event) => {
                event.stopPropagation();
                onClick?.();
            }}
        >
            {name}
        </button>
    );
}
