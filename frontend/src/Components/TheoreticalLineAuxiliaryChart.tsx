import { DetailsList, IColumn, SelectionMode, Stack, Selection, SpinButton, Slider, IconButton, MessageBarType, MessageBar } from "@fluentui/react";
import { useQuery } from "react-query";
import { useEffect, useRef, useState } from "react";
import { GroupWingModelData, WingModelData } from "../Model/OptionData";
import { CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from "recharts";
import DownwardTriangle from "../Utils/DownloadTriangle";
import { theoreticalDataProvider } from "../DataProvider/TheoreticalDataProvider";
import { optionDataProvider } from "../DataProvider/OptionDataProvider";

const drawWingModelLine = (
    volatility: number,
    k1: number,
    k2: number,
    b: number,
    step: number,
) => {

    if (volatility === undefined || k1 === undefined || k2 === undefined || b === undefined) {
        return [];
    }
    const result: { x: number; y: number }[] = [];
    const CUT_POINT = 3; // Define the cut-off point

    for (let xDistance = -CUT_POINT * step; xDistance < CUT_POINT * step; xDistance++) {
        const x = xDistance / step;
        const y =
            x < 0
                ? (volatility + k1 * x * x + b * x) * 100
                : (volatility + k2 * x * x + b * x) * 100;

        result.push({ x, y });
    }

    return result;
};


const TheoreticalLineAuxiliaryChart = () => {
    const [selectedItem, setSelectedItem] = useState<any>();
    const [selectedCffexCurveData, setSelectedCffexCurveData] = useState<{ x: number, y: number }[]>([]);
    const [selectedSeCurveData, setSelectedSeCurveData] = useState<{ x: number, y: number }[]>([]);
    const [selectedCurCurveData, setSelectedCurCurveData] = useState<{ x: number, y: number }[]>([]);
    const [shadowCurveData, setShadowCurveData] = useState<{ x: number, y: number }[]>([]);
    const [shadowWingPara, setShadowWingPara] = useState<Record<string, WingModelData>>({});

    const [notification, setNotification] = useState<{ message: string; type: MessageBarType } | null>(null);

    const { data: tableData = [] } = useQuery(
        ['fetchWingModelData'],
        () => theoreticalDataProvider.fetchWingModelData(),
        {
            select(data) {
                return data.map((item: GroupWingModelData) => ({
                    "name": item.name,
                    "cffex_symbol": item.cffex?.symbol ?? null,
                    "cffex_v": item.cffex?.v ?? null,
                    "cffex_k1": item.cffex?.k1 ?? null,
                    "cffex_k2": item.cffex?.k2 ?? null,
                    "cffex_b": item.cffex?.b ?? null,

                    "se_symbol": item.se?.symbol ?? null,
                    "se_v": item.se?.v ?? null,
                    "se_k1": item.se?.k1 ?? null,
                    "se_k2": item.se?.k2 ?? null,
                    "se_b": item.se?.b ?? null,

                    "avg_v": item.average?.v ?? null,
                    "avg_k1": item.average?.k1 ?? null,
                    "avg_k2": item.average?.k2 ?? null,
                    "avg_b": item.average?.b ?? null,

                    "cur_v": item.current?.v ?? null,
                    "cur_k1": item.current?.k1 ?? null,
                    "cur_k2": item.current?.k2 ?? null,
                    "cur_b": item.current?.b ?? null,

                    "shadow_v": shadowWingPara[item.name]?.v ?? 0,
                    "shadow_k1": shadowWingPara[item.name]?.k1 ?? 0,
                    "shadow_k2": shadowWingPara[item.name]?.k2 ?? 0,
                    "shadow_b": shadowWingPara[item.name]?.b ?? 0,

                }));
            },
            onSuccess(data) {
                // console.log("fetchWingModelData" + JSON.stringify(data))
            },
            refetchInterval: 10000,
            refetchOnWindowFocus: false,
        }
    );

    useEffect(() => {
        if (selectedItem?.cffex_symbol) {
            setSelectedCffexCurveData(drawWingModelLine(selectedItem?.cffex_v, selectedItem?.cffex_k1, selectedItem?.cffex_k2, selectedItem?.cffex_b, 20))
        }
    }, [selectedItem?.cffex_v, selectedItem?.cffex_b, selectedItem?.cffex_k1, selectedItem?.cffex_k2, selectedItem?.cffex_symbol])

    useEffect(() => {
        if (selectedItem?.se_symbol) {
            setSelectedSeCurveData(drawWingModelLine(selectedItem?.se_v, selectedItem?.se_k1, selectedItem?.se_k2, selectedItem?.se_b, 20))
        }
    }, [selectedItem?.se_v, selectedItem?.se_b, selectedItem?.se_k1, selectedItem?.se_k2, selectedItem?.se_symbol])

    useEffect(() => {
        if (selectedItem?.shadow_v !== 0) {
            setShadowCurveData(drawWingModelLine(selectedItem?.shadow_v, selectedItem?.shadow_k1, selectedItem?.shadow_k2, selectedItem?.shadow_b, 10));
        }
    }, [selectedItem?.shadow_k1, selectedItem?.shadow_k2, selectedItem?.shadow_b, selectedItem?.shadow_v]);

    useEffect(() => {
        if (selectedItem?.cur_v !== 0) {
            setSelectedCurCurveData(drawWingModelLine(selectedItem?.cur_v, selectedItem?.cur_k1, selectedItem?.cur_k2, selectedItem?.cur_b, 10));
        }
    }, [selectedItem?.cur_k1, selectedItem?.cur_k2, selectedItem?.cur_b, selectedItem?.cur_v]);

    const { data: cffexIVData } = useQuery(
        ["fetchIVData", selectedItem?.cffex_symbol],
        () => theoreticalDataProvider.fetchIVData(selectedItem?.cffex_symbol),
        {
            select(data) {
                return Object.entries(data).map(([strike, [x_distance, iv_ask, iv_bid]]) => ({
                    strike: strike,
                    x: x_distance,   // X轴：行权价标准差距离
                    iv_ask: iv_ask * 100,
                    iv_bid: iv_bid * 100,
                }));
            },
            enabled: !!selectedItem && !!selectedItem.cffex_symbol,
            refetchInterval: 10000,
            refetchOnWindowFocus: false,
        }
    );

    const { data: seIVData } = useQuery(
        ["fetchIVData", selectedItem?.se_symbol],
        () => theoreticalDataProvider.fetchIVData(selectedItem?.se_symbol),
        {
            select(data) {
                return Object.entries(data).map(([strike, [x_distance, iv_ask, iv_bid]]) => ({
                    strike: strike,
                    x: x_distance,   // X轴：行权价标准差距离
                    iv_ask: iv_ask * 100,
                    iv_bid: iv_bid * 100,
                }));
            },
            enabled: !!selectedItem && !!selectedItem.se_symbol,
            refetchInterval: 10000,
            refetchOnWindowFocus: false,
        }
    );


    const generateColumns = () => {
        const categories = ['cffex', 'se', 'avg', 'cur'];
        const subFields = ['v', 'k1', 'k2', 'b'];

        let columns: IColumn[] = [
            { key: 'name', name: '品种', fieldName: 'name', minWidth: 80, maxWidth: 100, isResizable: true }
        ];

        categories.forEach(category => {
            subFields.forEach(field => {
                columns.push({
                    key: `${category}_${field}`,
                    name: `${category} - ${field}`,
                    fieldName: `${category}_${field}`,
                    minWidth: 80,
                    maxWidth: 100,
                    isResizable: true,
                    onRender: (item) => {
                        const value = item[`${category}_${field}`];
                        return typeof value === 'number' ? (value * 100).toFixed(2) + '%' : value || "--";
                    }
                });
            });
        });

        subFields.forEach(field => {
            columns.push({
                key: `shadow_${field}`,
                name: `shadow - ${field}`,
                fieldName: `shadow_${field}`,
                minWidth: 80,
                maxWidth: 100,
                isResizable: true,
                onRender: (item) => {
                    const key = `${field}` as keyof WingModelData; // Explicitly cast
                    const rawValue = Number(shadowWingPara[item.name]?.[key] ?? 0); // 确保有默认值
                    const displayValue = !isNaN(rawValue) ? (rawValue * 100).toFixed(2) + " %" : "0%";
                    return (
                        <SpinButton
                            value={displayValue} // 这里是 formatted 后的显示值
                            min={-100}
                            max={100}
                            onIncrement={(newValue) => {
                                const sanitizedValue = newValue.replace('%', '').trim();
                                let updatedValue = parseFloat(sanitizedValue) / 100 + 0.001;
                                if (updatedValue > 1) updatedValue = 1;

                                setShadowWingPara(prev => {
                                    const newParams = {
                                        ...prev[item.name],
                                        [key]: updatedValue
                                    };
                                    return { ...prev, [item.name]: newParams };
                                });

                                return (updatedValue * 100).toFixed(2) + " %"; // 保持 UI 一致
                            }}
                            onDecrement={(newValue) => {
                                const sanitizedValue = newValue.replace('%', '').trim();
                                let updatedValue = parseFloat(sanitizedValue) / 100 - 0.001;
                                if (updatedValue < -1) updatedValue = -1;

                                setShadowWingPara(prev => {
                                    const newParams = {
                                        ...prev[item.name],
                                        [key]: updatedValue
                                    };
                                    return { ...prev, [item.name]: newParams };
                                });

                                return (updatedValue * 100).toFixed(2) + " %";
                            }}
                            onChange={(_, newValue) => {
                                if (!newValue) return; // 处理空值情况

                                const sanitizedValue = newValue.replace('%', '').trim();
                                let parsedValue = parseFloat(sanitizedValue) / 100;

                                if (isNaN(parsedValue)) return; // 防止 NaN 进入状态

                                // 限制数值范围
                                parsedValue = Math.max(-1, Math.min(1, parsedValue));

                                setShadowWingPara(prev => {
                                    const newParams = {
                                        ...prev[item.name],
                                        [key]: parsedValue
                                    };
                                    return { ...prev, [item.name]: newParams };
                                });
                            }}
                        />
                    );
                }
            });
        })

        columns.push({
            key: 'copy',
            name: '复制',
            fieldName: 'copy',
            minWidth: 50,
            maxWidth: 80,
            isResizable: true,
            onRender: (item) => {
                return (
                    <IconButton
                        iconProps={{ iconName: "Copy" }}
                        onClick={() => {
                            setShadowWingPara(prev => ({
                                ...prev,
                                [item.name]: {
                                    v: item.avg_v ?? 0,
                                    k1: item.avg_k1 ?? 0,
                                    k2: item.avg_k2 ?? 0,
                                    b: item.avg_b ?? 0
                                }
                            }));
                        }}
                    />
                );
            }
        });

        columns.push({
            key: 'confirm',
            name: '确定',
            fieldName: 'confirm',
            minWidth: 50,
            maxWidth: 80,
            isResizable: true,
            onRender: (item) => {
                return (
                    <IconButton
                        iconProps={{ iconName: "CheckMark" }}
                        onClick={async () => {
                            try {
                                await optionDataProvider.postWingModelPara({
                                    symbol: item.name,
                                    v: item.shadow_v ?? 0,
                                    k1: item.shadow_k1 ?? 0,
                                    k2: item.shadow_k2 ?? 0,
                                    b: item.shadow_b ?? 0,
                                    atm_available: 1
                                });
                                setNotification({ message: "自定义设置成功", type: MessageBarType.success });
                            } catch {
                                setNotification({ message: "Failed to send data", type: MessageBarType.error });
                            }
                        }}
                    />
                );
            }
        });

        return columns;
    };

    const selectionRef = useRef(
        new Selection({
            onSelectionChanged() {
                const selectedItem = selection.getSelection()[0] as any;
                if (selectedItem) {
                    setSelectedItem(selectedItem)
                }
            },
        })
    );
    const selection = selectionRef.current;


    useEffect(() => {
        // console.log('selectedBoxSpreadStrike: ' + selectedBoxSpreadStrike)
        const index = tableData.findIndex((item) => item.name === selectedItem?.name);
        if (index >= 0 && !selection.isIndexSelected(index)) {
            selection.setIndexSelected(index, true, false);
        }
    }, [tableData, selectedItem, selection])

    // useEffect(() => {
    //     console.log("selectedItem" + JSON.stringify(selectedItem))
    //     console.log("shadowCurveData" + JSON.stringify(shadowCurveData))
    //     // console.log("selectedItem" + selectedItem?.shadow_k1 + selectedItem?.shadow_k2 + selectedItem?.shadow_b);
    // }, [selectedItem])


    useEffect(() => {
        console.log("shadowCurveData" + JSON.stringify(shadowCurveData))
        // console.log("selectedItem" + selectedItem?.shadow_k1 + selectedItem?.shadow_k2 + selectedItem?.shadow_b);
    }, [shadowCurveData])

    const [activeLine, setActiveLine] = useState<string | null>(null);

    const [domainMin, setDominMin] = useState<number>(10);
    const [domainMax, setDominMax] = useState<number>(30);

    // const CustomTooltip = ({ active, label, payload, item }: any) => {
    //     if (!active || !payload || payload.length === 0) {
    //         return null;
    //     }

    //     const filteredPayload = payload.filter((item: any) => item.payload.strike !== undefined);

    //     if (filteredPayload.length === 0) {
    //         return null; // 或者返回一个空的 Tooltip
    //     }

    //     console.log("payload" + JSON.stringify(payload))
    //     console.log("label" + JSON.stringify(label))
    //     console.log("filteredPayload" + JSON.stringify(filteredPayload))

    //     return (
    //         <div className="custom-tooltip">
    //             {filteredPayload.map((item: any, index: any) => {
    //                 const { x, cffex_y, se_y, strike } = item.payload;
    //                 return (
    //                     <div key={index}>
    //                         <p>{`Strike: ${strike}`}</p>
    //                         <p>{`X: ${x}`}</p>
    //                         {cffex_y !== undefined && <p>{`Y: ${cffex_y}`}</p>}
    //                         {se_y !== undefined && <p>{`Y: ${se_y}`}</p>}
    //                     </div>
    //                 );
    //             })}
    //         </div>
    //     );
    // };



    return (
        <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: "100%", height: "100vh" } }}>
            <Stack.Item styles={{ root: { width: "100%", height: "50%" } }}>
                <DetailsList
                    columns={generateColumns()}
                    items={tableData || []}
                    selection={selection}
                    selectionMode={SelectionMode.single}
                />
            </Stack.Item>

            <Stack.Item>
                {notification && (
                    <MessageBar
                        messageBarType={notification.type}
                        isMultiline={false}
                        onDismiss={() => setNotification(null)}
                    >
                        {notification.message}
                    </MessageBar>
                )}
            </Stack.Item>

            <Stack.Item styles={{ root: { width: "100%", height: "40%" } }}>
                <Slider
                    min={0}
                    max={100}
                    step={5}
                    valueFormat={(v) => `${v}%`}
                    ranged
                    lowerValue={domainMin}
                    value={domainMax}
                    showValue
                    onChange={(value, range) => {
                        if (range) {
                            setDominMin(range[0])
                            setDominMax(range[1])
                        }
                    }}
                ></Slider>
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart>
                        <CartesianGrid strokeDasharray="3 3" />
                        <Tooltip />
                        {/* <Tooltip content={<CustomTooltip />} /> */}
                        <XAxis
                            orientation="top"
                            type="number"
                            dataKey="x"
                            ticks={[-2.6, -1.9, -1.3, -0.6, 0, 0.6, 1.3, 2.6]}
                            name="行权价" />
                        <YAxis
                            type="number"
                            name="Volatility (%)"
                            tickFormatter={(value) => `${value.toFixed(0)}%`}
                            domain={[domainMin, domainMax]}
                        />
                        <Legend onMouseEnter={(e) => setActiveLine(e.value)} onMouseLeave={() => setActiveLine(null)} />
                        <Scatter
                            name={`CFFEX - ${selectedItem?.cffex_symbol} - ask`}
                            data={cffexIVData?.map(point => ({ x: point.x, cffex_y: point.iv_ask, strike: point.strike })) ?? []}
                            shape={DownwardTriangle}
                            color="red"
                            dataKey="cffex_y"
                            fill="red"
                            opacity={activeLine && activeLine !== `CFFEX - ${selectedItem?.cffex_symbol} - ask` ? 0.2 : 1}
                        />
                        <Scatter
                            name={`CFFEX - ${selectedItem?.cffex_symbol} - bid`}
                            data={cffexIVData?.map(point => ({ x: point.x, cffex_y: point.iv_bid, strike: point.strike })) ?? []}
                            shape="triangle"
                            color="red"
                            dataKey="cffex_y"
                            fill="red"
                            opacity={activeLine && activeLine !== `CFFEX - ${selectedItem?.cffex_symbol} - bid` ? 0.2 : 1}
                        />
                        <Scatter
                            name={`SE - ${selectedItem?.se_symbol} - ask`}
                            data={seIVData?.map(point => ({ x: point.x, se_y: point.iv_ask, strike: point.strike })) ?? []}
                            shape={DownwardTriangle}
                            color="blue"
                            dataKey="se_y"
                            fill="blue"
                            opacity={activeLine && activeLine !== `SE - ${selectedItem?.se_symbol} - ask` ? 0.2 : 1}
                        />
                        <Scatter
                            name={`SE - ${selectedItem?.se_symbol} - bid`}
                            data={seIVData?.map(point => ({ x: point.x, se_y: point.iv_bid, strike: point.strike })) ?? []}
                            shape="triangle"
                            color="blue"
                            dataKey="se_y"
                            fill="blue"
                            opacity={activeLine && activeLine !== `SE - ${selectedItem?.se_symbol} - bid` ? 0.2 : 1}
                        />
                        {selectedItem?.cffex_symbol !== null && (
                            <Line
                                name={`CFFEX - ${selectedItem?.cffex_symbol} - FIT`}
                                type="monotone"
                                dataKey="y"
                                activeDot={false}
                                tooltipType="none"
                                dot={false}
                                stroke="red"
                                data={selectedCffexCurveData}
                                opacity={activeLine && activeLine !== `SE - ${selectedItem?.cffex_symbol} - FIT` ? 0.2 : 1}
                            />
                        )}
                        {selectedItem?.se_symbol !== null && (
                            <Line
                                name={`SE - ${selectedItem?.se_symbol} - FIT`}
                                type="monotone"
                                dataKey="y"
                                activeDot={false}
                                tooltipType="none"
                                dot={false}
                                stroke="blue"
                                data={selectedSeCurveData}
                                opacity={activeLine && activeLine !== `SE - ${selectedItem?.se_symbol} - FIT` ? 0.2 : 1}
                            />
                        )}
                        {selectedItem?.cur_v !== 0 && (
                            <Line
                                name={`CUR - FIT`}
                                type="monotone"
                                dataKey="y"
                                activeDot={false}
                                tooltipType="none"
                                dot={false}
                                stroke="green"
                                data={selectedCurCurveData}
                                opacity={activeLine && activeLine !== `CUR - FIT` ? 0.2 : 1}
                            />
                        )}
                        <Line
                            name="Shadow"
                            type="monotone"
                            dataKey="y"
                            activeDot={false}
                            dot={false}
                            tooltipType="none"
                            data={shadowCurveData}
                            stroke="white"
                            strokeDasharray="5 5"
                            opacity={activeLine && activeLine !== `Shadow` ? 0.2 : 1}
                        />
                    </ComposedChart>
                </ResponsiveContainer>
            </Stack.Item>
        </Stack>
    )
}

export default TheoreticalLineAuxiliaryChart;