
class NotesController < ApplicationController
    before_action :note_exists?, only: :show
    before_action :valid_note_id?, only: :show
    before_action :valid_attributes?, only: :create

    def new
    end

    def show
        existing_note
    end

    def create
        Rails.cache.write("/notes/#{new_note.id}", Marshal.dump(new_note), expires_in: 5.minutes)
        redirect_to action: "show", id: new_note.id
    end

    private

    def note_id
        @note_id ||= params[:id]
    end

    def note_data
        @note_data ||= Rails.cache.read("/notes/#{note_id}")
    end

    def existing_note
        @existing_note ||= Marshal.load(note_data)
    end

    def note_params
        @note_params ||= params.require(:note).permit(:author, :body)
    end

    def new_note
        @new_note ||= Note.new(**note_params.to_h.symbolize_keys)
    end

    def valid_note_id?
        raise ActionController::BadRequest.new("invalid note id") if note_id&.count("^a-z0-9") > 0
    end

    def note_exists?
        raise ActionController::RoutingError.new("note not found") unless note_data
    end

    def valid_attributes?
        raise ActionController::BadRequest.new("invalid attributes") if note_params[:author].length + note_params[:body].length > 500
    end

end
