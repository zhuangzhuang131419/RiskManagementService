import { DetailsList, DetailsListLayoutMode, IColumn, SelectionMode, DetailsRow, IDetailsRowStyles, Selection } from '@fluentui/react';
import React from 'react';

// 定义 ScrollBox 的通用 Props
interface ScrollBoxProps<T> {
  items: T[];
  onClick: (item: T) => void;
  renderItem: (item: T) => string; // 用于渲染每一项的显示内容
  title: string;
}

const ScrollBox = <T extends unknown>({ items, onClick, renderItem, title }: ScrollBoxProps<T>) => {
  // 自定义样式：只允许上下滚动
  const scrollBoxStyle: React.CSSProperties = {
    maxHeight: '100%', // 限制高度以产生滚动条
    maxWidth: '100%',
    overflowY: 'auto',  // 只允许上下滚动
    overflowX: 'hidden', // 禁止左右滚动
  };

  const columns: IColumn[] = [
    {
      key: 'column1',
      name: title,
      fieldName: 'item',
      minWidth: 10,
      maxWidth: 200,
      isResizable: true,
      onRender: (item: T, index?: number) => (
        <div>{renderItem(item)}</div> // Custom rendering for each row item
      ),
    },
  ];

  const selection = new Selection({
    onSelectionChanged: () => {
      const selectedItems = selection.getSelection();
      if (selectedItems.length > 0) {
        const selectedItem = selectedItems[0] as T;
        onClick(selectedItem); // 将选中的期权符号传递给父组件
      }
    },
  });

  return (
    <div style={scrollBoxStyle}>
      <DetailsList
        items={items}
        columns={columns}
        layoutMode={DetailsListLayoutMode.justified}
        selectionMode={SelectionMode.single}
        selection={selection}
        selectionPreservedOnEmptyClick={true}
        compact={true}
      />
    </div>
  );
};

export default ScrollBox;
