import { Dropdown, MessageBar, MessageBarType, Stack } from "@fluentui/react";
import { User } from "../Model/User";
import { useState } from "react";
import { userDataProvider } from "../DataProvider/UserDataProvider";



// 定义组件的 props 类型
interface UserSelectorProps {
  accounts: User[];               // accounts 为账户对象数组
  onSelect: (accountId: string) => void; // onSelect 函数接受选中的账户 ID
  selectedUserKey: string | null;
}

const UserSelector: React.FC<UserSelectorProps> = ({ accounts, onSelect, selectedUserKey }) => {
  // 保存当前选中的基准类型
  const [selectedUser, setSelectedUser] = useState<string | null>(selectedUserKey);
  const [message, setMessage] = useState<{ text: string; type: MessageBarType } | null>(null);

  const accountOptions = accounts.map((acc) => ({
    key: acc.id,
    text: acc.name,
  }));

  const onUserChange = async (userkey: string, userName: string) => {
    onSelect(userkey);
    setMessage(null); // 清除之前的消息


    try {
      userDataProvider.setUser(userName)
      setMessage({ text: `用户 ${userName} 已成功选择。`, type: MessageBarType.success });
    } catch (error) {
      // console.log("setUser:" + error)
      setMessage({ text: `选择用户 ${userName} 时出错: ${error}`, type: MessageBarType.error });
    } finally {
      setTimeout(() => setMessage(null), 3000); // 3秒后消失
    }
    setSelectedUser(userkey)
  }

  return (
    <Stack>
      <Dropdown
        placeholder="选择账户"
        label="账户"
        selectedKey={selectedUser}
        options={accountOptions}
        onChange={(event, option) => onUserChange(option?.key as string, option?.text as string)}
        styles={{ root: { width: "300px" } }}
      />
      {message && (
        <MessageBar messageBarType={message.type}>
          {message.text}
        </MessageBar>
      )}
    </Stack>


  );
};

export default UserSelector;