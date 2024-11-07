import React from 'react';
import { DetailsList, DetailsListLayoutMode, IColumn, SelectionMode } from '@fluentui/react';

const UserInfoTable = () => {
    // Define the columns for the table
    const columns: IColumn[] = [
        { key: 'column1', name: '账户类型', fieldName: 'accountType', minWidth: 100, maxWidth: 150, isRowHeader: true },
        { key: 'column2', name: '权益', fieldName: 'equity', minWidth: 150, maxWidth: 200 },
        { key: 'column3', name: '可用资金', fieldName: 'availableFunds', minWidth: 150, maxWidth: 200 },
        { key: 'column4', name: '风险度', fieldName: 'riskLevel', minWidth: 100, maxWidth: 150 },
    ];

    // Define the data for the table rows
    const items = [
        {
            key: 'row1',
            accountType: '期货账户',
            equity: '',
            availableFunds: '',
            riskLevel: '',
        },
        {
            key: 'row2',
            accountType: 'ETF期权账户',
            equity: '',
            availableFunds: '',
            riskLevel: '',
        },
        {
            key: 'row3',
            accountType: '合计',
            equity: '',
            availableFunds: '',
            riskLevel: '无',
        },
    ];

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
