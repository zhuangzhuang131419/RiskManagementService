import React from 'react';

interface ScatterShapeProps {
    cx?: number;
    cy?: number;
    fill?: string;
}

const DownwardTriangle = (props: { cx?: number; cy?: number; fill?: string }) => {
    const { cx = 0, cy = 0, fill = "black" } = props;
    const size = 10; // 控制三角形大小
    return (
        <svg x={cx - size} y={cy - size} width={size * 2} height={size * 2} viewBox="0 0 24 24">
            <polygon points="12,20 4,6 20,6" fill={fill} />
        </svg>
    );
};


export default DownwardTriangle;
