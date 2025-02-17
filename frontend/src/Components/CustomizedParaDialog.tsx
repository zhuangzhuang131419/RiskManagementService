import React, { useState } from 'react';
import { TextField, Stack, Panel, DefaultButton, PrimaryButton, DetailsList, DetailsListLayoutMode, SelectionMode, IColumn, PanelType, MessageBarType, MessageBar } from '@fluentui/react';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';
import { useQuery } from 'react-query';
import { WingModelData } from '../Model/OptionData';

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

    const [updatedRows, setUpdatedRows] = useState<ICustomizedParaItem[]>([])

    const [notification, setNotification] = useState<{ message: string; type: MessageBarType } | null>(null);

    const { isLoading, error, refetch } = useQuery(
        'wingModelData',
        optionDataProvider.fetchWingModelPara,
        {
            select(data) {
                // 转换数据为 rows 数组格式
                const rows = data
                    ? Object.entries(data).map(([symbol, values]) => ({
                        symbol,
                        v: values.v,
                        k1: values.k1,
                        k2: values.k2,
                        b: values.b
                    }))
                    : [];
                return rows;
            },
            onSuccess(data) {
                console.log('fetchWingModelPara onsuccess:' + JSON.stringify(data))
                setRows(data)
            },
        }
    );

    const renderItem = (symbol: string) => {
        const prefix = symbol.slice(0, symbol.length - 8);
        const year = symbol.slice(symbol.length - 6, symbol.length - 4);
        const month = symbol.slice(symbol.length - 4, symbol.length - 2);
        return `${prefix}${year}${month}`;
    }

    const columns: IColumn[] = [
        {
            key: 'symbol', name: '品种', fieldName: 'symbol', minWidth: 100, onRender: (item, index?: number) => (
                <div>{renderItem(item.symbol)}</div> // Custom rendering for each row item
            ),
        },
        { key: 'v', name: 'v', fieldName: 'v', minWidth: 50 },
        { key: 'k1', name: 'k1', fieldName: 'k1', minWidth: 50 },
        { key: 'k2', name: 'k2', fieldName: 'k2', minWidth: 50 },
        { key: 'b', name: 'b', fieldName: 'b', minWidth: 50 }
    ];

    const onhandleComfirm = async () => {
        console.log('updatedRows:' + JSON.stringify(updatedRows))

        const para: { [key: string]: WingModelData } = updatedRows.reduce((acc, item) => {
            acc[item.symbol] = {
                v: item.v,
                k1: item.k1,
                k2: item.k2,
                b: item.b,
                atm_vol: 0, // 如果需要其他字段，例如 atm_vol，可以在这里添加
                atm_available: 1 // 根据需求设置默认值
            };
            return acc;
        }, {} as { [key: string]: WingModelData });

        console.log('para:' + JSON.stringify(para))


        try {
            await optionDataProvider.postWingModelPara(para);
            setNotification({ message: "Data successfully sent to the server", type: MessageBarType.success });
        } catch (error) {
            setNotification({ message: "Failed to send data", type: MessageBarType.error });
        } finally {
            setUpdatedRows([])
            refresh();
            setTimeout(() => setNotification(null), 3000); // 3秒后消失
        }
    }

    const onhandleCancel = async () => {
        const para: { [key: string]: WingModelData } = rows.reduce((acc, item) => {
            acc[item.symbol] = {
                v: 0,
                k1: 0,
                k2: 0,
                b: 0,
                atm_vol: 0, // 如果需要其他字段，例如 atm_vol，可以在这里添加
                atm_available: 1 // 根据需求设置默认值
            };
            return acc;
        }, {} as { [key: string]: WingModelData });

        console.log('para:' + JSON.stringify(para))


        try {
            await optionDataProvider.postWingModelPara(para);
            setNotification({ message: "Data successfully sent to the server", type: MessageBarType.success });
        } catch (error) {
            setNotification({ message: "Failed to send data", type: MessageBarType.error });
        } finally {
            setUpdatedRows([])
            refresh()
        }
    }

    const refresh = async () => {
        closePanel();
        refetch();
    }

    return (
        <Stack horizontalAlign="stretch">
            <DefaultButton onClick={() => setIsPanelOpen(true)} text="Open Panel" />

            {notification && (
                <MessageBar
                    messageBarType={notification.type}
                    isMultiline={false}
                    onDismiss={() => setNotification(null)}
                >
                    {notification.message}
                </MessageBar>
            )}


            <Panel
                isOpen={isPanelOpen}
                onDismiss={refresh}
                headerText="手动设置参数"
                isFooterAtBottom={true}
                onRenderFooterContent={() => (
                    <Stack horizontal tokens={{ childrenGap: 10 }} horizontalAlign="end">
                        <PrimaryButton onClick={onhandleComfirm} text="确定" />
                        <DefaultButton onClick={onhandleCancel} text="清空" />
                    </Stack>
                )}
                type={PanelType.medium} // 设置为大型面板，或者使用 PanelType.custom 来自定义大小
                styles={{
                    main: {
                        maxWidth: '40vw', // 控制 Panel 的最大宽度
                    },
                }}
            >
                {!isLoading && !error && (
                    <Stack>
                        <DetailsList
                            items={rows}
                            columns={columns}
                            isHeaderVisible={true}
                            selectionMode={SelectionMode.none}
                            layoutMode={DetailsListLayoutMode.justified}
                            onRenderItemColumn={(item, index, column) => {
                                if (!column || !column.fieldName) return null;
                                const fieldName = column.fieldName as keyof ICustomizedParaItem;

                                return (
                                    <TextField
                                        defaultValue={String(item[fieldName])}
                                        onChange={(e, newValue) => {
                                            updatedRows[index as number] = { ...updatedRows[index as number], [fieldName]: newValue, symbol: rows[index as number].symbol };
                                            rows[index as number] = { ...rows[index as number], [fieldName]: newValue };
                                        }}
                                        disabled={fieldName === 'symbol'}
                                    />
                                );
                            }}
                        />
                    </Stack>)
                }
            </Panel>
        </Stack>
    );
};

export default CustomizedParaDialog;
