import React, { useState } from 'react';
import { TextField, Stack, Panel, DefaultButton, PrimaryButton, ScrollablePane, DetailsList, DetailsListLayoutMode, SelectionMode, IColumn, PanelType } from '@fluentui/react';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import { QueryClient, QueryClientProvider, useQuery } from 'react-query';

interface CustomizedParaDialogProps {
    style?: React.CSSProperties;
}

export interface ICustomizedParaItem {
    symbol: string;
    v: number;
    k1: number;
    k2: number;
    b: number;
}

const CustomizedParaDialog: React.FC<CustomizedParaDialogProps> = ({ style }) => {
    const [isPanelOpen, setIsPanelOpen] = useState<boolean>(false);

    const closePanel = () => setIsPanelOpen(false);

    const [rows, setRows] = useState<ICustomizedParaItem[]>([])

    const { data, isLoading, error } = useQuery(
        'wingModelData',
        optionDataProvider.fetchWingModelPara,
        {
            select(data) {
                console.log('data:' + data)

                // 转换数据为 rows 数组格式
                return data
                    ? Object.entries(data).map(([symbol, values]) => ({
                        symbol,
                        v: values.v,
                        k1: values.k1,
                        k2: values.k2,
                        b: values.b
                    }))
                    : [];
            },
            onSuccess() {
                console.log('data:' + data)
                setRows(data as ICustomizedParaItem[])
            }
        }
    );

    const columns: IColumn[] = [
        { key: 'symbol', name: '品种', fieldName: 'symbol', minWidth: 100 },
        { key: 'v', name: 'v', fieldName: 'v', minWidth: 50 },
        { key: 'k1', name: 'k1', fieldName: 'k1', minWidth: 50 },
        { key: 'k2', name: 'k2', fieldName: 'k2', minWidth: 50 },
        { key: 'b', name: 'b', fieldName: 'b', minWidth: 50 }
    ];

    return (
        <Stack horizontalAlign="stretch">
            <DefaultButton onClick={() => setIsPanelOpen(true)} text="Open Panel" />

            <Panel
                isOpen={isPanelOpen}
                onDismiss={closePanel}
                headerText="手动设置参数"
                closeButtonAriaLabel="Close"
                type={PanelType.medium} // 设置为大型面板，或者使用 PanelType.custom 来自定义大小
                styles={{
                    main: {
                        maxWidth: '40vw', // 控制 Panel 的最大宽度
                    },
                }}
            >
                <ScrollablePane>
                    <DetailsList
                        items={rows}
                        columns={columns}
                        selectionMode={SelectionMode.none}
                        layoutMode={DetailsListLayoutMode.justified}
                        onRenderItemColumn={(item, index, column) => {
                            if (!column || !column.fieldName) return null;
                            const fieldName = column.fieldName as keyof ICustomizedParaItem;
                            return (
                                <TextField
                                    value={String(item[fieldName])}
                                    onChange={(e, newValue) => {
                                        const updatedRows = [...rows];
                                        updatedRows[index as number] = { ...updatedRows[index as number], [fieldName]: Number(newValue) || 0 };
                                        setRows(updatedRows);
                                    }}
                                    disabled={column.fieldName === 'symbol'}
                                />
                            );
                        }}
                    />
                </ScrollablePane>

                <Stack horizontal tokens={{ childrenGap: 10, padding: 10 }} horizontalAlign="end" style={{ position: 'absolute', bottom: 10, right: 10 }}>
                    <PrimaryButton onClick={closePanel} text="确定" />
                    <DefaultButton onClick={() => setRows(rows.map(row => ({ ...row, v: 0, k1: 0, k2: 0, b: 0 })))} text="清空" />
                </Stack>
            </Panel>
        </Stack>
    );
};

export default CustomizedParaDialog;
