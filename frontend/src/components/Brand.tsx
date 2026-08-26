import "./Brand.css";

type BrandProps = {
    size?: "sm" | "md" | "lg";
};

export function Brand({ size = "md" }: BrandProps) {
    const sizes = {
        sm: "1rem",
        md: "1.5rem",
        lg: "2rem",
    };

    return (
        <div className="brand" style={{ fontSize: sizes[size] }}>
            <img
                src="/projboard-icon.svg"
                alt="ProjBoard"
                style={{ width: "1em", height: "1em" }}
            />
            <span>ProjBoard</span>
        </div>
    );
}
