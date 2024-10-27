import { DetailsList, SelectionMode, Stack, Text } from '@fluentui/react';
import { WingModelData } from '../Model/OptionData';

interface WingModelProps {
    data: WingModelData[]
}


const WingModelBar: React.FC<WingModelProps> = ({ data }) => {
  

  const columns = [
    { key: 'atmVol', name: 'ATM波动率', fieldName: 'atm_vol', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'k1', name: 'K1', fieldName: 'k1', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'k2', name: 'K2', fieldName: 'k2', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'b', name: 'b', fieldName: 'b', minWidth: 100, maxWidth: 150, isResizable: true },
    { key: 'atmAvailable', name: 'ATM 可用性', fieldName: 'atm_available', minWidth: 100, maxWidth: 150, isResizable: true },
];
  
  return (
    <DetailsList
      items={data}
      selectionMode={SelectionMode.none}
      columns={columns}
    />
  );
};

export default WingModelBar;
