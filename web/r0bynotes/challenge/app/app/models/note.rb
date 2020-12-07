class Note
    attr_accessor :author, :body, :date, :id

    def initialize(author:, body:, date: Time.now)
        @id = SecureRandom.hex
        @author = author
        @body = body
        @date = date
    end
end
