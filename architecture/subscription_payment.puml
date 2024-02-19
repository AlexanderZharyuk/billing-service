@startuml
participant Client          as user
participant Billing         as service
database    Database        as db 
participant Worker          as worker
participant PaymentProvider as pp


user -> service: Инициирует обновление подписки из ЛК
service -> db: - Обновляет объект **Subscription** \n- Создает объект **Invoice**
service -> worker: Создает задачу на прием статуса платежа
service -> pp: (POST) Создает платеж
pp -[#blue]> worker: pending-статус платежа
worker -> service: Отправляет статус платежа
service -> db: Создает объект **Payment** \nсо статусом pending
service -> user: Передает URL для оплаты
user -> pp: подтверждает оплату (вводит данные)
pp -[#green]> worker: succeeded-статус платежа
worker -> service: Отправляет статус платежа
service -> db: Обновляет объект **Payment** \nсо статусом <font color=green>succeeded</font>
service -> user: Отдает URL для возврата в ЛК
@enduml
