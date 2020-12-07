Rails.application.routes.draw do
    resources :notes, only: [:new, :show, :create]
    resources :users, only: [:new, :show, :create]

    get 'welcome/index'
    root 'welcome#index'
end
