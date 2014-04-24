create table music_artist (
		`id` int unsigned primary key auto_increment,
		`name` text not null
);

create table music_album (
		`id` int unsigned primary key auto_increment,
		`name` text not null,
		`artist_id` int unsigned,
		foreign key (`artist_id`)
			references `music_artist` (`id`)
	);

create table music_song (
		`id` int unsigned primary key auto_increment,
		`title` text not null,
		`year` int unsigned,
		`tracknumber` int unsigned,
		`path` text not null,
		`times_played` int unsigned,
		`album_id` int unsigned,
		`artist_id` int unsigned,
		foreign key (`artist_id`)
			references `music_artist` (`id`),
		foreign key (`album_id`)
			references `music_album` (`id`)
);

