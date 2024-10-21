import { Dropdown } from "@fluentui/react";

interface Account {
    id: string;
    name: string;
  }
  
  // 定义组件的 props 类型
  interface AccountSelectorProps {
    accounts: Account[];               // accounts 为账户对象数组
    onSelect: (accountId: string) => void; // onSelect 函数接受选中的账户 ID
  }

const AccountSelector: React.FC<AccountSelectorProps> = ({ accounts, onSelect }) => {
    const accountOptions = accounts.map((acc) => ({
      key: acc.id,
      text: acc.name,
    }));
  
    return (
      <Dropdown
        placeholder="选择账户"
        label="账户"
        options={accountOptions}
        onChange={(event, option) => onSelect(option?.key as string)}
        styles={{ dropdown: { width: 300 } }}  // 设置下拉框宽度
      />
    );
  };
  
  export default AccountSelector;