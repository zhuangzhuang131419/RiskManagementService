import { DetailsList, DetailsListLayoutMode, IColumn, SelectionMode, Selection, IDetailsListStyles } from '@fluentui/react';
import { useEffect, useRef, useState } from 'react';

// 定义 ScrollBox 的通用 Props
interface ScrollBoxProps<T> {
  items: T[];
  onClick: (key: string | null) => void;
  renderItem: (item: T) => string; // 用于渲染每一项的显示内容
  title: string;
  selectedItemKey: string | null;
}

const ScrollBox = <T extends { key: string }>({ items, onClick, renderItem, title, selectedItemKey }: ScrollBoxProps<T>) => {

  const [selectedItem, setSelectedItem] = useState<string | null>(selectedItemKey);

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

  const selectionRef = useRef(
    new Selection({
      onSelectionChanged: () => {
        const selectedItems = selection.getSelection();
        if (selectedItems.length > 0) {
          const selectedItem = selectedItems[0] as T;
          onClick(selectedItem.key);
          setSelectedItem(selectedItem.key)
        }
        else {
          onClick(null);
          setSelectedItem(null)
        }
      },
    })
  );
  const selection = selectionRef.current;

  useEffect(() => {
    const index = items.findIndex((item) => item.key === selectedItem);
    if (index >= 0) {
      selection.setIndexSelected(index, true, false);
      setSelectedItem(selectedItem); // 更新本地 `selectedItem` 状态
    }
  }, [selectedItem, selection, items])

  const gridStyles: Partial<IDetailsListStyles> = {
    root: {
      overflowX: 'hidden', // 禁止左右滚动
      overflowY: 'auto',
      height: '100%'
    },
    headerWrapper: {
      position: 'sticky', // 表头固定
      top: 0, // 距顶部的距离
      zIndex: 1, // 确保表头在内容上方
    },
  };

  return (
    <DetailsList
      items={items}
      columns={columns}
      layoutMode={DetailsListLayoutMode.justified}
      selectionMode={SelectionMode.single}
      selection={selection}
      selectionPreservedOnEmptyClick={true}
      compact={true}
      styles={gridStyles}
    />
  );
};

export default ScrollBox;
