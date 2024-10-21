import { List, Text } from '@fluentui/react';
import React from 'react';

// 定义 ScrollBox 的通用 Props
interface ScrollBoxProps<T> {
  items: T[];
  onClick: (item: T) => void;
  renderItem: (item: T) => string; // 用于渲染每一项的显示内容
}

const ScrollBox = <T extends unknown>({ items, onClick, renderItem }: ScrollBoxProps<T>) => {
  // 自定义样式：只允许上下滚动
  const scrollBoxStyle: React.CSSProperties = {
    maxHeight: '300px', // 限制高度以产生滚动条
    overflowY: 'auto',  // 只允许上下滚动
    overflowX: 'hidden', // 禁止左右滚动
  };

  return (
    <div style={scrollBoxStyle}>
      <List
        items={items}
        onRenderCell={(item) => (
            <div onClick={() => onClick(item as T)} style={{ padding: '8px', cursor: 'pointer' }}>
              <Text>{renderItem(item as T)}</Text>
            </div>
          )}
      />
    </div>
  );
};

export default ScrollBox;
