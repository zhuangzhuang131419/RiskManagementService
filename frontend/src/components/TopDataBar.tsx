import { DetailsList, SelectionMode, Stack, Text } from '@fluentui/react';
import { TopBarData } from '../Model/Account';

interface TopDataBarProps {
  data: TopBarData[]
}


const TopDataBar: React.FC<TopDataBarProps> = ({ data }) => {


  const columns = [
    { key: 'greekLetter', name: '希腊字母', fieldName: 'greekLetter', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'indexOption', name: '指数期权', fieldName: 'indexOption', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'etfOption', name: 'ETF期权', fieldName: 'etfOption', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'futures', name: '期货', fieldName: 'futures', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'cash', name: '现金', fieldName: 'cash', minWidth: 100, maxWidth: 150, isResizable: true },
  ];

  return (
    // <Stack horizontal>
    //   <Text>{`希腊字母: ${data.greekLetters}`}</Text>
    //   <Text>{`指数期权数量: ${data.indexOptionCount}`}</Text>
    //   <Text>{`ETF期权数量: ${data.etfOptionCount}`}</Text>
    //   <Text>{`期货数量: ${data.futureCount}`}</Text>
    //   <Text>{`现金结合: ${data.cashCombined}`}</Text>
    // </Stack>

    <DetailsList
      items={data}
      selectionMode={SelectionMode.none}
      columns={columns}
    />
  );
};

export default TopDataBar;
