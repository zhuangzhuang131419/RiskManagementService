import { Stack, Text } from '@fluentui/react';
import { TopBarData } from '../Model/Account';

interface TopDataBarProps {
    data: TopBarData
}


const TopDataBar: React.FC<TopDataBarProps> = ({ data }) => {
  return (
    <Stack horizontal>
      <Text>{`希腊字母: ${data.greekLetters}`}</Text>
      <Text>{`指数期权数量: ${data.indexOptionCount}`}</Text>
      <Text>{`ETF期权数量: ${data.etfOptionCount}`}</Text>
      <Text>{`期货数量: ${data.futureCount}`}</Text>
      <Text>{`现金结合: ${data.cashCombined}`}</Text>
    </Stack>
  );
};

export default TopDataBar;
