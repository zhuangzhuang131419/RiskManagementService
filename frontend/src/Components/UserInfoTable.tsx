import React, { useEffect, useState } from 'react';
import { DetailsList, DetailsListLayoutMode, IColumn, SelectionMode } from '@fluentui/react';
import { useQuery } from 'react-query';
import { optionDataProvider } from '../DataProvider/OptionDataProvider';

interface UserInfoTableProps {
    indexSymbol: string
    etfSymbol: string
}

const UserInfoTable: React.FC<UserInfoTableProps> = ({ indexSymbol, etfSymbol }) => {

    const [items, setItems] = useState<any[]>([
        { key: 'index', accountType: '期货账户', equity: '—', availableFunds: '—', riskLevel: '—' },
        { key: 'etf', accountType: 'ETF期权账户', equity: '—', availableFunds: '—', riskLevel: '—' },
        { key: 'row3', accountType: '合计', equity: '—', availableFunds: '—', riskLevel: '无' },
    ]);

    // Define the columns for the table
    const columns: IColumn[] = [
        { key: 'column1', name: '账户类型', fieldName: 'accountType', minWidth: 100, maxWidth: 150, isRowHeader: true },
        // { key: 'column2', name: '权益', fieldName: 'equity', minWidth: 150, maxWidth: 200 },
        // { key: 'column3', name: '可用资金', fieldName: 'availableFunds', minWidth: 150, maxWidth: 200 },
        { key: 'column4', name: '风险度', fieldName: 'riskLevel', minWidth: 100, maxWidth: 150 },
    ];

    const { data: indexRiskLevel } = useQuery(
        ['indexOptionMonitor', indexSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
        () => optionDataProvider.fetchIndexOptionMonitor(indexSymbol as string),
        {
            onSuccess(data) {
                console.log('fetchIndexOptionMonitor: ' + JSON.stringify(data))
            },
            enabled: !!indexSymbol,  // 只有当 symbol 存在时才启用查询
            refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
            refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
        }
    );

    const { data: etfRiskLevel } = useQuery(
        ['etfOptionMonitor', etfSymbol],  // symbol 作为查询的 key，symbol 变化时会重新加载
        () => optionDataProvider.fetchETFOptionMonitor(etfSymbol as string),
        {
            onSuccess(data) {
                console.log('fetchETFOptionMonitor: ' + JSON.stringify(data))
            },
            enabled: !!etfSymbol,  // 只有当 symbol 存在时才启用查询
            refetchOnWindowFocus: false, // 禁用在窗口获得焦点时重新获取数据
            refetchInterval: 3000, // 每隔 3 秒重新获取一次数据
        }
    );

    useEffect(() => {
        const updatedItems = items.map((item) =>
            item.key === 'index'
                ? { ...item, riskLevel: indexRiskLevel ?? '—' } // Update riskLevel for row1
                : item
        );

        console.log("useEffect" + JSON.stringify(updatedItems))

        setItems(updatedItems); // Set the updated array
    }, [indexRiskLevel]);

    useEffect(() => {
        const updatedItems = items.map((item) =>
            item.key === 'etf'
                ? { ...item, riskLevel: etfRiskLevel ?? '—' } // Update riskLevel for row1
                : item
        );

        setItems(updatedItems); // Set the updated array
    }, [etfRiskLevel]);




    return (
        <DetailsList
            items={items}
            columns={columns}
            selectionMode={SelectionMode.none}
            layoutMode={DetailsListLayoutMode.fixedColumns}
            selectionPreservedOnEmptyClick
        />
    );
};

export default UserInfoTable;
