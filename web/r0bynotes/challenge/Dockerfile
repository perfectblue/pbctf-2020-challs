FROM ruby:2.7.2

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list

RUN apt-get update -qq && apt-get install -y nodejs yarn

WORKDIR /app
COPY ./app/Gemfile /app/Gemfile
COPY ./app/Gemfile.lock /app/Gemfile.lock
RUN bundle install
COPY ./app /app

# Add a script to be executed every time the container starts.
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
EXPOSE 3000

COPY ./flag.txt /flag.txt
RUN chmod 400 /flag.txt

COPY ./read_flag /read_flag
RUN chmod 4555 /read_flag

RUN useradd --home-dir /app app
RUN chown -R app:app /app

USER app

# comment out for dev mode
ENV RAILS_ENV production

# Start the main process.
CMD ["rails", "server", "-b", "0.0.0.0"]