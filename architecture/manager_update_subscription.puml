@startuml
participant Client          as user
participant Billing         as service
database    Database        as db 


user -> service: <font color=#7f7f7f>GET: </font> Инициирует обновление подписки 
service -> db: - Обновляет объект **Subscription**
service -> user: Возвращает статус операции
@enduml
