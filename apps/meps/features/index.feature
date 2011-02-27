Feature: Basic lettuce tests

    Scenario: Homepage
        Given I access the url "/"
        Then I see the header "Memopol"

    Scenario: Country list
        Given I access the url "/meps/countries"
        Then I see the header "MEPs by country"

    Scenario: Albert Dess
        Given I access the url "/meps/mep/AlbertDess"
        Then I see the header "Albert DESS, member of the european parliament"
	
    Scenario: Albert Dess Structure page
        Given I access the url "/meps/mep/AlbertDess/structure"
        Then I see the header "Memopol"

    Scenario: Albert Dess JSON
        Given I access the url "/meps/mep/AlbertDess/json"
        Then I get a response with content type "application/json"
