class MultiLanguageTextString:
	code: str
	chinese: str
	chineseTraditional: str
	english: str
	japanese: str
	korean: str

class ChartUnlock:
	unlockType: int
	unlockInfo: list[str]

class LevelMods:
	levelMods: list[str]

class AvatarInfo:
	getSong: int
	getType: int
	getPower: int
	getInfo1: str
	getInfo2: str
	getInfo3: str
	name: str
	addressableKey: str

class CollectionItemIndex:
	getSong: int
	getType: int
	getPower: int
	getInfo1: str
	getInfo2: str
	getInfo3: str
	key: str
	subIndex: int
	multiLanguageTitle: MultiLanguageTextString

class Key:
	keyName: str
	unlockedTimes: int
	kindOfKey: int
	unlockTimes: int

class SongsItem:
	songsId: str
	songsKey: str
	songsName: str
	songsTitle: str
	difficulty: list[float]
	illustrator: str
	charter: list[str]
	composer: str
	levels: list[str]
	previewTime: float
	previewEndTime: float
	unlockInfo: list[ChartUnlock]
	levelMods: list[LevelMods]
	isCnLimited: bool
	hasDifferentMusic: bool
	differentMusic: int
	previewClipDifficulty: int
	hasDifferentCover: bool
	differentCover: int

