import { Dropdown, IDropdownOption } from "@fluentui/react";


  
  // 定义组件的 props 类型
interface BaselineSelectorProps {
  onSelect: (accountId: string) => void; // onSelect 函数接受选中的账户 ID
}

const BaselineSelector: React.FC<BaselineSelectorProps> = ({ onSelect }) => {
    const options = [
        { key: 'average', text: '平均基准' },
        { key: 'shanghai', text: '上交基准' },
        { key: 'individual', text: '各自基准' },
    ];
  
    return (
      <Dropdown
        placeholder="选择基准"
        label="基准选择"
        options={options}
        onChange={(event, option) => onSelect(option?.key as string)}
        styles={{ dropdown: { width: 300 } }}  // 设置下拉框宽度
      />
    );
  };
  
  export default BaselineSelector;