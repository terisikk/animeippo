import pytest

from animeippo.providers import provider


def test_new_provider_can_be_instantiated():
    class ConcreteAnimeProvider(provider.AbstractAnimeProvider):
        def __init__(self):
            super().__init__()

        def get_user_anime_list(self, user_id):
            super().get_user_anime_list(user_id)

        def get_seasonal_anime_list(self, year, season):
            super().get_seasonal_anime_list(year, season)

        def get_features(self):
            super().get_features()

        def get_related_anime(self, id):
            super().get_related_anime(id)

    actual = ConcreteAnimeProvider()
    actual.get_user_anime_list(None)
    actual.get_seasonal_anime_list(None, None)
    actual.get_features()
    actual.get_related_anime(None)

    assert issubclass(actual.__class__, provider.AbstractAnimeProvider)


def test_new_provider_subclassing_fails_with_missing_methods():
    with pytest.raises(TypeError):

        class ConcreteAnimeProvider(provider.AbstractAnimeProvider):
            def __init__(self):
                pass

        ConcreteAnimeProvider()
