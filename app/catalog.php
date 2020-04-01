<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */


$titolofeed="Biblioteca Archimedica";
$sottotitolofeed="Sottotiolo Archimedico";
$licenzafeed="CC-BY-SA";
$mediaUrl="http://biblioteca.archimedica.eu/ebook";

$dbHost="localhost";
$dbUser="root";
$dbPass="4ottobre2009";

error_reporting(E_ALL);
ob_start();
include_once 'inc/class.AtomBuilder.inc.php';
// include_once 'utf8.php';
/* create new feed object with the required informations: title, url to feed, id of the feed */
$atom = new AtomBuilder($titolofeed, 'http://biblioteca.archimedica.eu', 'tag:io@archimedix.net,2009-12-29:http://biblioteca.archimedica.eu/catalog.php');
$atom->setEncoding('UTF-8'); // only needed if NOT utf-8 windows-1256
// $atom->setEncoding('latin1');
$atom->setLanguage('it'); // recommended, but not required
$atom->setSubtitle($sottotitolofeed); //optional
$atom->setRights($licenzafeed); //optional
$dateupdate= date('c', time());
$atom->setUpdated($dateupdate);
// $atom->setUpdated('2009-10-29T14:34:00.25Z'); // required !! last time the feed or one of it's entries was last modified/updated; in php5 you can use date('c', $timestamp) to generate a valid date
$atom->setAuthor('Archimedix', 'io@archimedix.net', 'http://www.archimedix.net'); // name required, email and url are optional
$atom->setIcon('http://biblioteca.archimedica.eu/img/Biblio_16x16.png'); // optional
$atom->setLogo('http://biblioteca.archimedica.eu/img/Biblio_100x86.png'); // optional
$atom->addContributor('Archimedix', 'io@qrchimedix.net', 'http://archimedix.tel');
/* you can add a lot of different links to the feed and it's entries, see intertwingly.net/wiki/pie/ for more infos */
$atom->addLink('http://php.net/', 'Official PHP homepage', 'related', 'text/html', 'en');
$atom->addLink('http://example.com/', 'Example.com – HTML Homepage', 'alternate', 'text/html', 'en');
$atom->addCategory('Webdesign', 'http://www.example.com/tags', 'Web 2.0 Webdesign'); // optional
$atom->addCategory('PHP'); // optional


$r=mysql_connect($dbHost, $dbUser, $dbPass);
mysql_select_db('1', $r);
$res = mysql_query("SELECT * FROM ebooks where epub=1 ORDER BY N DESC");
while ($data = mysql_fetch_object($res)) {

	//	$item = new FeedItem();
	$titolo = utf8_encode ($data->Titolo);
	$nomeURL = utf8_encode ($data->nomeURL);
	$autore = utf8_encode ($data->Autore);
	$sottotitolo = utf8_encode ($data->Sottotitolo);
	$descrizione = utf8_encode ($data->Descrizione);
	$licenza = utf8_encode ($data->LIC);
	$id= ($data->id);
	$entry = $atom->newEntry($titolo, 'http://example.com/permalink_item', "tag:archimedica,2010:feed/detail/$id");
        $entry->setAuthor($autore);
	$entry->setRights($licenza);
	$entry->setUpdated('2005-10-29T14:44:00Z');
	$entry->setSummary($sottotitolo, 'html');
	$entry->setContent($descrizione ,'html');
//	$entry->setContent('', 'application/epub+zip', "$mediaUrl/$nomeURL.epub");
// $entry->addLink("$mediaUrl/$nomeURL.epub", 'url', 'via', 'epub+zip', 'it')

$entry->addContributor('Archimedix', 'io@archimedix.net'); // optional
/* optional links */
$entry->addLink('http://www.meyerweb.com/', 'meyerweb.com', 'via', 'text/html', 'en'); // for example if you post your plog entry in reply to someone elses plog entry
$entry->addLink('http://orf.at/', 'ORF ON', 'related', 'text/html', 'de'); // related links for that entry
$entry->addLink('http://feedvalidator.org/', 'Feed Validator for RSS and ATOM', 'related', 'text/html', 'en');
$entry->addCategory('Webdesign', 'http://www.flaimo.com/tags', 'Web 2.0 Webdesign'); // optional
// $entry->setContent("http://www.archiatiedizioni.it/ebook/$nomeURL.png", 'image/jpg'); // you can also use other mime types
$atom->addEntry($entry); // add the created entry to the feed

}

// content can also be declared xhtml. but then your xhtml code has to be valid. invalid xhtml (xml) code will show an error message in the feed
//$entry_2->setContent('<p>The whole content of the entry. This <b>and</b> the summary <big>can contain XHTML</big></p>', 'xhtml');

/*
// you could also just link to the content
$entry_2->setContent('', 'application/pdf', 'http://flaimo.com/sample.pdf');
*/


$version = '1.0.0'; // 1.0 is the only version so far
$atom->outputAtom($version);

/*
// if you don't want to directly output the content, but instead work with the string (for example write it to a cache file) use
$foo = $atom->getAtomOutput($version);
*/

/*
// saves the xml file to the given path and returns the path + filename as a string
$path = '';
echo $atom->saveAtom($version, $path);
*/

ob_end_flush();
?>
