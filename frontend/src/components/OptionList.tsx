import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { Stack, DetailsList, DetailsListLayoutMode, IColumn, SelectionMode, DetailsRow, IDetailsRowStyles, Selection } from '@fluentui/react';

interface OptionListProps {
    onSelect: (symbol: string) => void;
}

interface OptionItem {
    key: string;
    symbol: string;
}

const fetchOptions = async () => {
    const response = await fetch('/api/options');
    if (!response.ok) {
        throw new Error('Failed to fetch options');
    }
    return response.json();
};

const OptionList: React.FC<OptionListProps> = ({ onSelect }) => {
    const [options, setOptions] = useState<OptionItem[]>([]);

    const { data, error, isFetching } = useQuery(['options'], fetchOptions, {
        onSuccess: (data: string[]) => {
            const optionItems = data.map((option) => ({
                key: option,
                symbol: option,
            }));
            setOptions(optionItems);
        }
    });

    const columns: IColumn[] = [
        { key: 'column1', name: '期权', fieldName: 'symbol', minWidth: 10, maxWidth: 200, isResizable: true },
    ];

    // 定义选择行为
    const selection = new Selection({
        onSelectionChanged: () => {
            const selectedItems = selection.getSelection() as OptionItem[];
            if (selectedItems.length > 0) {
                const selectedItem = selectedItems[0];
                onSelect(selectedItem.symbol); // 将选中的期权符号传递给父组件
            }
        },
    });

    const scrollBoxStyles = {
        root: {
            height: '300px',   // 固定高度
            overflowX: 'hidden', // 禁用水平滚动
            overflowY: 'auto', // 垂直滚动
            // border: '1px solid #ccc', // 可选：添加边框
            // padding: '10px',   // 内边距
        },
    };

    const onRenderRow = (props: any) => {
        const customRowStyles: Partial<IDetailsRowStyles> = {
            root: {
                paddingTop: 0,  // 调整行的上内边距
                paddingBottom: 0, // 调整行的下内边距
                height: 20,     // 调整行高（可选）
            },
        };
        return <DetailsRow {...props} styles={customRowStyles} />;
    };


    return (
        <DetailsList
            items={options}
            columns={columns}
            setKey="set"
            layoutMode={DetailsListLayoutMode.justified}
            selectionMode={SelectionMode.single}
            selection={selection}
            ariaLabelForSelectionColumn="Toggle selection"
            checkButtonAriaLabel="select row"
            styles={scrollBoxStyles}
            selectionPreservedOnEmptyClick={true}
            onRenderRow={onRenderRow}
        />
    );
};

export default OptionList;

