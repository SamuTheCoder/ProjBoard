import type { ReactNode } from "react";
import "./StatCard.css";

type StatCardProps = {
    value: number;
    label: string;
    icon?: ReactNode;
};

export function StatCard({ value, label, icon }: StatCardProps) {
    return (
        <div className="stat-card">
            {icon && <div className="stat-card-icon">{icon}</div>}

            <div>
                <strong>{value}</strong>
                <span>{label}</span>
            </div>
        </div>
    );
}
