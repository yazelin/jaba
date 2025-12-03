# ai-integration Spec Delta

## MODIFIED Requirements

### Requirement: AI 管理員動作 - 店家管理
AI 在管理模式下 SHALL 能夠透過 `update_store` 動作啟用或停用店家。

#### Scenario: 停用店家
- **GIVEN** 管理員說「把 xxx 店家停用」
- **WHEN** AI 執行 `update_store` 動作
- **AND** `action.data` 包含 `store_id` 和 `active: false`
- **THEN** 該店家被停用
- **AND** 不會出現在一般使用者的店家列表中

#### Scenario: 啟用店家
- **GIVEN** 管理員說「把 xxx 店家啟用」
- **WHEN** AI 執行 `update_store` 動作
- **AND** `action.data` 包含 `store_id` 和 `active: true`
- **THEN** 該店家被啟用
- **AND** 會出現在一般使用者的店家列表中
