
class UsersController < ApplicationController
    before_action :user_exists?, only: :show
    before_action :valid_user_id?, only: [:show, :create]
    before_action :valid_attributes?, only: :create

    def new
    end

    def show
        existing_user
    end

    def create
        Rails.cache.write(cache_key, user_params[:name], expires_in: 5.minutes)
        redirect_to action: "show", id: user_id
    end

    private
    def existing_user
        @existing_user ||= Rails.cache.read(cache_key)
    end

    def user_params
        @user_params ||= params.require(:user).permit(:username, :name)
    end

    def raw_user_id
        params[:id] || sprintf("#{user_params[:username]}%1$s", SecureRandom.hex)
    end

    def user_id
        @user_id ||= raw_user_id[0..100]
    end

    def cache_key
        @cache_key ||= user_id
    end

    def valid_user_id?
        raise ActionController::BadRequest.new("invalid username") if raw_user_id&.count("^a-z0-9") > 0
    end

    def user_exists?
        raise ActionController::RoutingError.new("user not found") unless existing_user
    end

    def valid_attributes?
        raise ActionController::BadRequest.new("invalid attributes") if user_params[:username].length + user_params[:name].length > 500
    end

end
